import re

import numpy as np

from api.database import get_connection
from rag.embeddings import create_embeddings

TOP_K = 5
YEAR_PATTERN = re.compile(r"\b(?:19|20)\d{2}\b")

COUNTRY_ALIASES = {
    "indian": "India",
    "american": "United States",
    "british": "United Kingdom",
    "korean": "South Korea",
}
GENRE_KEYWORDS = {
    "comedy": ("comedy",),
    "horror": ("horror",),
    "documentary": ("documentary",),
    "drama": ("drama",),
    "romance": ("romantic", "romance"),
    "crime": ("crime",),
    "thriller": ("thriller",),
    "anime": ("anime",),
    "children": ("children", "kids"),
}


def get_catalogue() -> list[dict]:
    """Load titles and their searchable metadata from SQLite."""
    connection = get_connection()

    rows = connection.execute(
        """
        SELECT
            t.show_id,
            t.type,
            t.title,
            t.release_year,
            t.rating,
            t.description,
            GROUP_CONCAT(DISTINCT c.name),
            GROUP_CONCAT(DISTINCT g.name)
        FROM titles t
        LEFT JOIN title_countries tc ON t.show_id = tc.show_id
        LEFT JOIN countries c ON tc.country_id = c.id
        LEFT JOIN title_genres tg ON t.show_id = tg.show_id
        LEFT JOIN genres g ON tg.genre_id = g.id
        GROUP BY
            t.show_id,
            t.type,
            t.title,
            t.release_year,
            t.rating,
            t.description
        """
    ).fetchall()

    connection.close()

    return [
        {
            "show_id": row[0],
            "type": row[1],
            "title": row[2],
            "release_year": row[3],
            "rating": row[4],
            "description": row[5] or "",
            "country": row[6] or "",
            "genres": row[7] or "",
        }
        for row in rows
    ]


def create_catalogue_text(title: dict) -> str:
    """Create the text representation used for embedding a title."""
    return (
        f"Title: {title['title']}\n"
        f"Type: {title['type']}\n"
        f"Country: {title['country']}\n"
        f"Genres: {title['genres']}\n"
        f"Release year: {title['release_year']}\n"
        f"Rating: {title['rating']}\n"
        f"Description: {title['description']}"
    )


def select_candidate_indices(question: str, catalogue: list[dict]) -> list[int]:
    """Select titles matching explicit type, country, genre, or year terms."""
    question_lower = question.lower()
    question_words = set(question_lower.replace("?", " ").split())
    requested_type: str | None = None

    if "movie" in question_words:
        requested_type = "Movie"
    elif "tv show" in question_lower or "tv series" in question_lower:
        requested_type = "TV Show"

    requested_countries = {
        country.lower()
        for country in COUNTRY_ALIASES.values()
        if country.lower() in question_lower
    }
    requested_countries.update(
        COUNTRY_ALIASES[word].lower()
        for word in question_words
        if word in COUNTRY_ALIASES
    )
    requested_genres = {
        keyword
        for keyword in GENRE_KEYWORDS
        if keyword in question_words
    }
    requested_years = {int(year) for year in YEAR_PATTERN.findall(question)}

    candidates: list[int] = []
    for index, title in enumerate(catalogue):
        title_countries = {country.strip().lower() for country in title["country"].split(",")}
        title_genres = title["genres"].lower()

        if requested_type and title["type"] != requested_type:
            continue
        if requested_countries and not requested_countries.intersection(title_countries):
            continue
        if requested_genres and not any(
            genre_word in title_genres
            for genre in requested_genres
            for genre_word in GENRE_KEYWORDS[genre]
        ):
            continue
        if requested_years and title["release_year"] not in requested_years:
            continue
        candidates.append(index)

    has_explicit_filter = any(
        (requested_type, requested_countries, requested_genres, requested_years)
    )
    return candidates if has_explicit_filter else list(range(len(catalogue)))

def retrieve_titles(
    question: str,
    catalogue: list[dict],
    catalogue_embeddings: np.ndarray,
) -> list[dict]:
    """Return the most relevant catalogue titles for a question."""
    candidate_indices = select_candidate_indices(question, catalogue)
    if not candidate_indices:
        return []

    question_embedding = create_embeddings([question])[0]
    candidate_embeddings = catalogue_embeddings[candidate_indices]
    scores = candidate_embeddings @ question_embedding
    top_positions = np.argsort(scores)[-TOP_K:][::-1]
    top_indices = [candidate_indices[position] for position in top_positions]

    return [
        {
            **catalogue[index],
            "score": float(scores[position]),
        }
        for position, index in zip(top_positions, top_indices)
    ]

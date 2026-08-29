import numpy as np

from api.database import get_connection
from rag.embeddings import create_embeddings

TOP_K = 5


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

def retrieve_titles(
    question: str,
    catalogue: list[dict],
    catalogue_embeddings: np.ndarray,
) -> list[dict]:
    """Return the most relevant catalogue titles for a question."""
    question_embedding = create_embeddings([question])[0]

    scores = catalogue_embeddings @ question_embedding

    question_lower = question.lower()

    if "movie" in question_lower:
        for index, title in enumerate(catalogue):
            if title["type"] != "Movie":
                scores[index] -= 0.2

    if "tv show" in question_lower or "tv series" in question_lower:
        for index, title in enumerate(catalogue):
            if title["type"] != "TV Show":
                scores[index] -= 0.2

    top_indices = np.argsort(scores)[-TOP_K:][::-1]

    return [
        {
            **catalogue[index],
            "score": float(scores[index]),
        }
        for index in top_indices
    ]
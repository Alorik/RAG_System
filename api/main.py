import os
import sqlite3

from enum import Enum
from pydantic import BaseModel, Field, field_validator

from rag.embeddings import create_embeddings
from rag.generation import GeminiUnavailableError, generate_answer
from rag.retrieval import (
    YEAR_PATTERN,
    create_catalogue_text,
    get_applied_filters,
    get_catalogue,
    retrieve_titles,
    select_candidate_indices,
)
from fastapi import FastAPI, HTTPException, Query

from api.database import get_connection


class TitleType(str, Enum):
    MOVIE = "Movie"
    TV_SHOW = "TV Show"

class AskRequest(BaseModel):
    question: str = Field(max_length=500)

    @field_validator("question")
    @classmethod
    def validate_question(cls, value: str) -> str:
        """Reject empty or meaningless questions and trim surrounding whitespace."""
        question = value.strip()
        if not question or not any(character.isalnum() for character in question):
            raise ValueError("Question must contain meaningful text")
        return question


app = FastAPI(title="Netflix Catalog API")
catalogue = get_catalogue()
catalogue_texts = [create_catalogue_text(title) for title in catalogue]
catalogue_embeddings = create_embeddings(catalogue_texts)


@app.get("/")
def root() -> dict[str, str]:
    """Return a simple response to confirm the API is running."""
    return {"message": "Netflix Catalog API is running"}


@app.get("/health")
def get_health() -> dict:
    """Report whether the database and Gemini configuration are available."""
    connection: sqlite3.Connection | None = None
    title_count: int | None = None

    try:
        connection = get_connection()
        title_count = connection.execute("SELECT COUNT(*) FROM titles").fetchone()[0]
    except sqlite3.Error:
        database_status = "unavailable"
    else:
        database_status = "available"
    finally:
        if connection is not None:
            connection.close()

    gemini_configured = bool(os.getenv("GEMINI_API_KEY"))
    if database_status == "unavailable":
        status = "unhealthy"
    elif not gemini_configured:
        status = "degraded"
    else:
        status = "healthy"

    return {
        "status": status,
        "database": database_status,
        "catalogue_titles": title_count,
        "gemini_configured": gemini_configured,
    }


@app.get("/titles")
def get_titles(
    country: str | None = None,
    release_year: int | None = None,
    type: TitleType | None = None,
    rating: str | None = None,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
) -> list[dict]:
    """Return paginated titles with optional filters."""
    connection = get_connection()

    query = """
        SELECT DISTINCT t.show_id, t.type, t.title, t.release_year, t.rating
        FROM titles t
    """

    conditions: list[str] = []
    params: list[str | int] = []

    if country:
        query += """
            JOIN title_countries tc ON t.show_id = tc.show_id
            JOIN countries c ON tc.country_id = c.id
        """
        conditions.append("c.name = ?")
        params.append(country)

    if release_year is not None:
        conditions.append("t.release_year = ?")
        params.append(release_year)

    if rating:
        conditions.append("t.rating = ?")
        params.append(rating)

    if type:
        conditions.append("t.type = ?")
        params.append(type)

    if conditions:
        query += " WHERE " + " AND ".join(conditions)

    query += " LIMIT ? OFFSET ?"
    params.extend([page_size, (page - 1) * page_size])

    rows = connection.execute(query, params).fetchall()
    connection.close()

    return [
        {
            "show_id": row[0],
            "type": row[1],
            "title": row[2],
            "release_year": row[3],
            "rating": row[4],
        }
        for row in rows
    ]


@app.get("/titles/{show_id}")
def get_title(show_id: int) -> dict:
    """Return a single title with its countries and genres."""
    connection = get_connection()

    row = connection.execute(
        """
        SELECT show_id, type, title, release_year, rating
        FROM titles
        WHERE show_id = ?
        """,
        (show_id,),
    ).fetchone()

    if row is None:
        connection.close()
        raise HTTPException(status_code=404, detail="Title not found")

    countries = connection.execute(
        """
        SELECT c.name
        FROM countries c
        JOIN title_countries tc ON c.id = tc.country_id
        WHERE tc.show_id = ?
        """,
        (show_id,),
    ).fetchall()

    genres = connection.execute(
        """
        SELECT g.name
        FROM genres g
        JOIN title_genres tg ON g.id = tg.genre_id
        WHERE tg.show_id = ?
        """,
        (show_id,),
    ).fetchall()

    connection.close()

    return {
        "show_id": row[0],
        "type": row[1],
        "title": row[2],
        "release_year": row[3],
        "rating": row[4],
        "countries": [country[0] for country in countries],
        "genres": [genre[0] for genre in genres],
    }


@app.get("/search")
def search_titles(
    q: str,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
) -> list[dict]:
    """Search titles by name with pagination."""
    connection = get_connection()

    rows = connection.execute(
        """
        SELECT show_id, type, title, release_year, rating
        FROM titles
        WHERE title LIKE ?
        LIMIT ? OFFSET ?
        """,
        (f"%{q}%", page_size, (page - 1) * page_size),
    ).fetchall()

    connection.close()

    return [
        {
            "show_id": row[0],
            "type": row[1],
            "title": row[2],
            "release_year": row[3],
            "rating": row[4],
        }
        for row in rows
    ]


@app.get("/stats")
def get_stats() -> dict:
    """Return summary statistics for the catalogue."""
    connection = get_connection()

    total_titles = connection.execute(
        "SELECT COUNT(*) FROM titles"
    ).fetchone()[0]

    type_rows = connection.execute(
        """
        SELECT type, COUNT(*)
        FROM titles
        GROUP BY type
        """
    ).fetchall()

    country_rows = connection.execute(
        """
        SELECT c.name, COUNT(DISTINCT tc.show_id)
        FROM countries c
        JOIN title_countries tc ON c.id = tc.country_id
        GROUP BY c.id, c.name
        ORDER BY COUNT(DISTINCT tc.show_id) DESC
        LIMIT 10
        """
    ).fetchall()

    connection.close()

    return {
        "total_titles": total_titles,
        "by_type": {
            row[0]: row[1]
            for row in type_rows
        },
        "top_countries": [
            {
                "country": row[0],
                "count": row[1],
            }
            for row in country_rows
        ],
    }

@app.post("/ask")
def ask_catalogue(request: AskRequest) -> dict:
    """Answer a natural-language question using retrieved catalogue titles."""
    applied_filters = get_applied_filters(request.question)
    candidate_indices = select_candidate_indices(request.question, catalogue)
    if not candidate_indices:
        requested_years = YEAR_PATTERN.findall(request.question)
        if requested_years:
            question_without_year = YEAR_PATTERN.sub("", request.question)
            related_count = len(
                select_candidate_indices(question_without_year, catalogue)
            )
            year_text = ", ".join(requested_years)
            return {
                "answer": (
                    f"There are {related_count} titles matching your other filters, "
                    f"but none were released in {year_text}."
                ),
                "match_count": 0,
                "related_match_count": related_count,
                "applied_filters": applied_filters,
                "sources": [],
            }
        return {
            "answer": "No catalogue titles match the filters in your question.",
            "match_count": 0,
            "applied_filters": applied_filters,
            "sources": [],
        }

    retrieved_titles = retrieve_titles(
        request.question,
        catalogue,
        catalogue_embeddings,
    )

    try:
        answer = generate_answer(
            request.question,
            retrieved_titles,
        )
    except GeminiUnavailableError:
        answer = (
            "Gemini is temporarily unavailable. "
            "Here are the most relevant catalogue matches."
        )

    return {
        "answer": answer,
        "match_count": len(candidate_indices),
        "applied_filters": applied_filters,
        "sources": [
            {
                "show_id": title["show_id"],
                "title": title["title"],
            }
            for title in retrieved_titles
        ],
    }

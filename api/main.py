from fastapi import FastAPI, Query, HTTPException
from enum import Enum
from api.database import get_connection

class TitleType(str, Enum):
    MOVIE = "Movie"
    TV_SHOW = "TV Show"

app = FastAPI(title="Netflix Catalog API")


@app.get("/")
def root() -> dict[str, str]:
    """Return a simple response to confirm the API is running."""
    return {"message": "Netflix Catalog API is running"}


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
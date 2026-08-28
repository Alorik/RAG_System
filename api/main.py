from fastapi import FastAPI

from api.database import get_connection

app = FastAPI(title="Netflix Catalog API")


@app.get("/")
def root() -> dict[str, str]:
    """Return a simple response to confirm the API is running."""
    return {"message": "Netflix Catalog API is running"}


@app.get("/titles")
def get_titles(
    page: int = 1,
    page_size: int = 20,
    ) -> list[dict]:

    """Return all titles from the Netflix catalogue."""
    connection = get_connection()

    rows = connection.execute(
        """
        SELECT show_id, type, title, release_year, rating
        FROM titles
        LIMIT ? OFFSET ?
        """,
        (page_size, (page - 1) * page_size),
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
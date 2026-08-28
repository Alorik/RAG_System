from fastapi import FastAPI

from api.database import get_connection

app = FastAPI(title="Netflix Catalog API")


@app.get("/")
def root() -> dict[str, str]:
    """Return a simple response to confirm the API is running."""
    return {"message": "Netflix Catalog API is running"}


@app.get("/titles")
def get_titles(
    country: str | None = None,
    page: int = 1,
    page_size: int = 20,
    ) -> list[dict]:
    """Return paginated titles with an optional country filter."""
    connection = get_connection()

    query = """
        SELECT DISTINCT t.show_id, t.type, t.title, t.release_year, t.rating
        FROM titles t
    """

    params: list[str | int] = []

    if country:
        query += """
            JOIN title_countries tc ON t.show_id = tc.show_id
            JOIN countries c ON tc.country_id = c.id
            WHERE c.name = ?
        """
        params.append(country)

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
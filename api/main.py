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
    release_year: int | None = None,
    type: str | None = None,
    page: int = 1,
    page_size: int = 20,
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
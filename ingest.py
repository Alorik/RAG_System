import csv
import sqlite3

from pathlib import Path
from datetime import datetime


CSV_PATH = Path("data/netflix_titles.csv")

DB_PATH = Path("data/netflix.db")

def load_csv() -> list[dict[str, str]]:
    """Load the Netflix titles from the source CSV."""
    with CSV_PATH.open("r", encoding="utf-8", newline="") as file:
        return list(csv.DictReader(file))

def normalize_date(value: str | None) -> str | None:
    """Convert a CSV date into ISO format while preserving missing values."""
    if value is None:
        return None

    return datetime.strptime(value, "%B %d, %Y").date().isoformat()

def clean_row(row: dict[str, str]) -> dict[str, str | None]:
    """Trim string values and convert empty values to None."""
    cleaned = {}

    for key, value in row.items():
        value = value.strip()
        cleaned[key] = value if value else None
      
    cleaned["show_id"] = int(cleaned["show_id"])
    cleaned["release_year"] = int(cleaned["release_year"])
    cleaned["date_added"] = normalize_date(cleaned["date_added"])  

    return cleaned


def create_database() -> sqlite3.Connection:
    """Create the SQLite database and its tables."""
    connection = sqlite3.connect(DB_PATH)

    connection.executescript(
        """
        CREATE TABLE IF NOT EXISTS titles (
            show_id INTEGER PRIMARY KEY,
            type TEXT NOT NULL,
            title TEXT NOT NULL,
            director TEXT,
            cast TEXT,
            date_added TEXT,
            release_year INTEGER NOT NULL,
            rating TEXT,
            duration TEXT,
            description TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS countries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE
        );

        CREATE TABLE IF NOT EXISTS title_countries (
            show_id INTEGER NOT NULL,
            country_id INTEGER NOT NULL,
            PRIMARY KEY (show_id, country_id),
            FOREIGN KEY (show_id) REFERENCES titles(show_id),
            FOREIGN KEY (country_id) REFERENCES countries(id)
        );

        CREATE TABLE IF NOT EXISTS genres (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE
        );

        CREATE TABLE IF NOT EXISTS title_genres (
            show_id INTEGER NOT NULL,
            genre_id INTEGER NOT NULL,
            PRIMARY KEY (show_id, genre_id),
            FOREIGN KEY (show_id) REFERENCES titles(show_id),
            FOREIGN KEY (genre_id) REFERENCES genres(id)
        );
        """
    )

    return connection



def insert_titles(
    connection: sqlite3.Connection,
    rows: list[dict[str, str | int | None]],
) -> None:
    """Insert cleaned title records into the titles table."""
    connection.executemany(
        """
        INSERT INTO titles (
            show_id,
            type,
            title,
            director,
            cast,
            date_added,
            release_year,
            rating,
            duration,
            description
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        [
            (
                row["show_id"],
                row["type"],
                row["title"],
                row["director"],
                row["cast"],
                row["date_added"],
                row["release_year"],
                row["rating"],
                row["duration"],
                row["description"],
            )
            for row in rows
        ],
    )

    connection.commit()

def split_values(value: str | None) -> list[str]:
    """Split a comma-separated field into cleaned individual values."""
    if value is None:
        return []

    return [item.strip() for item in value.split(",") if item.strip()]

def insert_countries(
    connection: sqlite3.Connection,
    rows: list[dict[str, str | int | None]],
) -> None:
    """Insert unique countries and link them to their titles."""
    for row in rows:
        countries = split_values(row["country"])

        for country in countries:
            connection.execute(
                "INSERT OR IGNORE INTO countries (name) VALUES (?)",
                (country,),
            )

            country_id = connection.execute(
                "SELECT id FROM countries WHERE name = ?",
                (country,),
            ).fetchone()[0]

            connection.execute(
                """
                INSERT INTO title_countries (show_id, country_id)
                VALUES (?, ?)
                """,
                (row["show_id"], country_id),
            )

    connection.commit()


def insert_genres(
    connection: sqlite3.Connection,
    rows: list[dict[str, str | int | None]],
) -> None:
    """Insert unique genres and link them to their titles."""
    for row in rows:
        genres = split_values(row["listed_in"])

        for genre in genres:
            connection.execute(
                "INSERT OR IGNORE INTO genres (name) VALUES (?)",
                (genre,),
            )

            genre_id = connection.execute(
                "SELECT id FROM genres WHERE name = ?",
                (genre,),
            ).fetchone()[0]

            connection.execute(
                """
                INSERT INTO title_genres (show_id, genre_id)
                VALUES (?, ?)
                """,
                (row["show_id"], genre_id),
            )

    connection.commit()

def print_summary(
    total_rows: int,
    cleaned_rows: int,
    dropped_rows: int,
) -> None:
    """Print a summary of the ingestion process."""
    print("\nIngestion Summary")
    print("-----------------")
    print(f"Rows loaded: {total_rows}")
    print(f"Rows cleaned: {cleaned_rows}")
    print(f"Rows dropped: {dropped_rows}")


def main() -> None:
    rows = load_csv()
    cleaned_rows = [clean_row(row) for row in rows]

    connection = create_database()
    insert_titles(connection, cleaned_rows)
    insert_countries(connection, cleaned_rows)
    insert_genres(connection, cleaned_rows)
    connection.close()

    print_summary(

        total_rows=len(rows),
        cleaned_rows=len(cleaned_rows),
        dropped_rows=0,
    )

if __name__ == "__main__":
    main()
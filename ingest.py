import csv
from pathlib import Path
from datetime import datetime


CSV_PATH = Path("data/netflix_titles.csv")


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


def main() -> None:
    rows = load_csv()
    cleaned_rows = [clean_row(row) for row in rows]

    print(f"Loaded {len(rows)} rows")
    print(cleaned_rows[0])


if __name__ == "__main__":
    main()
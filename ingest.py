import csv
from pathlib import Path

CSV_PATH = Path("data/netflix_titles.csv")


def load_csv() -> list[dict[str, str]]:
    """Load the Netflix titles from the source CSV."""
    with CSV_PATH.open("r", encoding="utf-8", newline="") as file:
        return list(csv.DictReader(file))


def main() -> None:
    rows = load_csv()
    print(f"Loaded {len(rows)} rows")


if __name__ == "__main__":
    main()
# Netflix Catalog Q&A System

## Setup

Python 3.10+ is required.

Create and activate a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate

Install the dependencies:

pip install -r requirements.txt


How to run
Data ingestion
Run:

python3 ingest.py

This loads the Netflix CSV, cleans and normalises the data, and creates the SQLite database at:
data/netflix.db

The script also prints an ingestion summary when it finishes.

API

Coming soon.

RAG Q&A

Coming soon.

How to test

Coming soon.

Known limitations

* The API has not been implemented yet.
* The RAG-based Q&A system has not been implemented yet.


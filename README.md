# Netflix Catalog Q&A System

A small Netflix catalogue API with structured search and natural-language
question answering using a basic RAG pipeline.

The project uses the provided Netflix titles CSV, SQLite for structured data,
Sentence Transformers for semantic retrieval, and Gemini for answer
generation.

## Setup

Python 3.10+ is required.

Create and activate a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Install the dependencies:

```bash
pip install -r requirements.txt
```

For the RAG Q&A endpoint, create a `.env` file in the project root:

```env
GEMINI_API_KEY=your_api_key_here
```

The API key is not committed to the repository.

## How to run

### Data ingestion

Run:

```bash
python ingest.py
```

This loads the Netflix CSV, cleans and normalises the data, and creates the
SQLite database at `data/netflix.db`.

The script prints a summary containing the number of rows loaded, fixed,
dropped, and any anomalies found.

### API

Start the FastAPI server:

```bash
uvicorn api.main:app --reload
```

The API will be available at:

```text
http://127.0.0.1:8000
```

Interactive API documentation is available at:

```text
http://127.0.0.1:8000/docs
```

### RAG Q&A

The natural-language Q&A endpoint is:

```text
POST /ask
```

Example request:

```json
{
  "question": "Suggest an Indian comedy movie"
}
```

The response contains a generated answer, the count of titles matching any
explicit question filters, and the `show_id` and title of each retrieved source.

## How to test

Run the complete automated test suite:

```bash
pytest -v
```

The current test suite contains 10 tests covering the API and RAG retrieval
behaviour.



## Project context

As in interview, I discussed that I have never worked with python or RAG systems,
So I just wanted to demonstrate that I can work with an unfamiliar technology.

This is what I did in the given time frame for the assignment. I hope it reaches you well.


## Known limitations

- Catalogue embeddings are generated when the API starts, so startup is
  relatively slow.
- Embeddings are kept in memory rather than persisted in a vector database.
- The RAG pipeline retrieves a fixed top-k set from metadata-filtered
  candidates when the question contains a supported type, country, genre, or
  release-year filter.
- Gemini generation requires an API key and network access.
- The current system is designed for the provided catalogue size and would
  need architectural changes for much larger datasets.

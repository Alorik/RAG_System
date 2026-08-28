from fastapi import FastAPI

app = FastAPI(title="Netflix Catalog API")


@app.get("/")
def root() -> dict[str, str]:
    """Return a simple response to confirm the API is running."""
    return {"message": "Netflix Catalog API is running"}
import os

from dotenv import load_dotenv
from google import genai
from google.genai import errors

load_dotenv()

MODEL_NAME = "gemini-3.6-flash"


class GeminiUnavailableError(RuntimeError):
    """Raised when Gemini cannot be configured or reached."""


def create_client() -> genai.Client:
    """Create a Gemini client using the API key from the environment."""
    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        raise GeminiUnavailableError("GEMINI_API_KEY is not configured")

    return genai.Client(api_key=api_key)


def generate_answer(question: str, titles: list[dict]) -> str:
    """Generate an answer using only the retrieved catalogue titles."""
    client = create_client()

    context = "\n\n".join(
        (
            f"Show ID: {title['show_id']}\n"
            f"Title: {title['title']}\n"
            f"Type: {title['type']}\n"
            f"Country: {title['country']}\n"
            f"Genres: {title['genres']}\n"
            f"Release year: {title['release_year']}\n"
            f"Rating: {title['rating']}\n"
            f"Description: {title['description']}"
        )
        for title in titles
    )

    prompt = f"""
You are a Netflix catalogue assistant.

Answer the user's question using ONLY the catalogue information
provided below.

Do not invent titles, facts, genres, countries, actors, or other
information that is not present in the context.

If the catalogue does not contain enough information to answer the
question, say so clearly.

When recommending titles, mention their exact title and show ID.

User question:
{question}

Catalogue context:
{context}
"""

    try:
        interaction = client.interactions.create(
            model=MODEL_NAME,
            input=prompt,
        )
    except errors.APIError as error:
        raise GeminiUnavailableError(
            "Gemini is temporarily unavailable. Please try again shortly."
        ) from error

    return interaction.output_text or "I could not generate an answer."

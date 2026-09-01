from fastapi.testclient import TestClient

from api.main import app
from rag.generation import GeminiUnavailableError


client = TestClient(app)


def test_root():
    response = client.get("/")

    assert response.status_code == 200
    assert response.json()["message"] == "Netflix Catalog API is running"


def test_get_titles():
    response = client.get("/titles")

    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert len(response.json()) <= 20


def test_filter_titles_by_country():
    response = client.get("/titles?country=India")

    assert response.status_code == 200

    for title in response.json():
        assert title["show_id"]
        assert title["title"]


def test_get_existing_title():
    response = client.get("/titles/80097355")

    assert response.status_code == 200
    assert response.json()["show_id"] == 80097355


def test_get_missing_title():
    response = client.get("/titles/999999999")

    assert response.status_code == 404


def test_search_titles():
    response = client.get("/search?q=Brahman")

    assert response.status_code == 200
    assert len(response.json()) >= 1
    assert any(
        title["title"] == "Brahman Naman"
        for title in response.json()
    )


def test_ask_returns_answer_and_sources(monkeypatch):
    def fake_generate_answer(question, titles):
        return "Brahman Naman is an Indian comedy movie."

    monkeypatch.setattr(
        "api.main.generate_answer",
        fake_generate_answer,
    )

    response = client.post(
        "/ask",
        json={"question": "Suggest an Indian comedy movie"},
    )

    assert response.status_code == 200

    data = response.json()

    assert data["answer"] == "Brahman Naman is an Indian comedy movie."
    assert data["match_count"] > 0
    assert data["applied_filters"] == {
        "type": "Movie",
        "countries": ["India"],
        "genres": ["comedy"],
    }
    assert "sources" in data
    assert len(data["sources"]) > 0
    assert "show_id" in data["sources"][0]
    assert "title" in data["sources"][0]


def test_ask_returns_no_sources_when_filters_have_no_matches():
    response = client.post(
        "/ask",
        json={"question": "Suggest an Indian movie from 2022"},
    )

    assert response.status_code == 200
    assert response.json()["match_count"] == 0
    assert response.json()["related_match_count"] > 0
    assert "but none were released in 2022" in response.json()["answer"]
    assert response.json()["applied_filters"]["release_years"] == [2022]
    assert response.json()["sources"] == []


def test_ask_returns_catalogue_matches_when_gemini_is_unavailable(monkeypatch):
    def fake_generate_answer(question, titles):
        raise GeminiUnavailableError("GEMINI_API_KEY is not configured")

    monkeypatch.setattr("api.main.generate_answer", fake_generate_answer)

    response = client.post(
        "/ask",
        json={"question": "Suggest an Indian comedy movie"},
    )

    assert response.status_code == 200
    assert response.json()["answer"] == (
        "Gemini is temporarily unavailable. "
        "Here are the most relevant catalogue matches."
    )
    assert len(response.json()["sources"]) > 0


def test_ask_rejects_a_question_with_no_meaningful_text():
    response = client.post("/ask", json={"question": " ?! "})

    assert response.status_code == 422


def test_ask_rejects_an_overly_long_question():
    response = client.post("/ask", json={"question": "a" * 501})

    assert response.status_code == 422

from fastapi.testclient import TestClient

from api.main import app


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
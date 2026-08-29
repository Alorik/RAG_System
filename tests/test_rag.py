from rag.retrieval import create_catalogue_text, get_catalogue, retrieve_titles
from rag.embeddings import create_embeddings


def test_catalogue_is_loaded():
    catalogue = get_catalogue()

    assert len(catalogue) == 6234


def test_catalogue_text_contains_metadata():
    catalogue = get_catalogue()
    text = create_catalogue_text(catalogue[0])

    assert "Title:" in text
    assert "Type:" in text
    assert "Country:" in text
    assert "Genres:" in text
    assert "Release year:" in text
    assert "Rating:" in text
    assert "Description:" in text


def test_retrieve_titles_returns_relevant_results():
    catalogue = get_catalogue()

    texts = [create_catalogue_text(title) for title in catalogue]
    embeddings = create_embeddings(texts)

    results = retrieve_titles(
        "Indian comedy movie",
        catalogue,
        embeddings,
    )

    assert len(results) == 5
    assert all("show_id" in result for result in results)
    assert all("title" in result for result in results)
    assert all("score" in result for result in results)
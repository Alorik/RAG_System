from rag.embeddings import create_embeddings
from rag.retrieval import create_catalogue_text, get_catalogue, retrieve_titles


catalogue = get_catalogue()

texts = [create_catalogue_text(title) for title in catalogue]

embeddings = create_embeddings(texts)

results = retrieve_titles(
    "Indian crime TV show",
    catalogue,
    embeddings,
)

for result in results:
    print(result["show_id"], result["title"], result["score"])
from rag.generation import generate_answer


titles = [
    {
        "show_id": "80097355",
        "title": "Brahman Naman",
        "type": "Movie",
        "country": "India",
        "genres": "Comedies, International Movies",
        "release_year": 2016,
        "rating": "TV-MA",
        "description": "A college student and his friends compete in a quiz competition.",
    }
]


answer = generate_answer(
    "Suggest an Indian comedy movie.",
    titles,
)

print(answer)
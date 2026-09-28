import requests

movies = [
    "Avatar",
    "Pirates of the Caribbean: At World's End",
    "Spectre",
    "The Dark Knight Rises",
    "John Carter",
    "Spider-Man 3",
    "Tangled",
    "Avengers: Age of Ultron",
    "Harry Potter and the Half-Blood Prince",
    "Batman v Superman: Dawn of Justice"
]

for movie in movies:

    url = "https://www.omdbapi.com/"

    params = {
        "t": movie,
        "apikey": "564727fa"
    }

    try:
        response = requests.get(url, params=params, timeout=10)
        data = response.json()

        if data.get("Response") == "True":
            print(movie)
            print("POSTER:", data.get("Poster"))
            print()

        else:
            print(movie, "→ Poster not found")

    except Exception as e:
        print(movie, "→ Error:", e)
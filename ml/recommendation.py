import pandas as pd
import ast

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


# =========================================================
# LOAD DATA
# =========================================================

movies = pd.read_csv(
    "data/clean_movies.csv"
)


# =========================================================
# CONVERT LIST STRINGS INTO TEXT
# =========================================================

def convert_to_text(value):

    try:

        if pd.isna(value):
            return ""

        # Convert string representation of list
        if isinstance(value, str):

            try:
                value = ast.literal_eval(value)
            except:
                return value

        if isinstance(value, list):

            return " ".join(
                str(item)
                for item in value
            )

        return str(value)

    except:

        return ""


# =========================================================
# PREPARE FEATURES
# =========================================================

movies["genres_text"] = movies[
    "genres"
].apply(convert_to_text)


movies["keywords_text"] = movies[
    "keywords"
].apply(convert_to_text)


movies["cast_text"] = movies[
    "cast"
].apply(convert_to_text)


movies["director_text"] = movies[
    "director"
].apply(convert_to_text)


movies["overview_text"] = movies[
    "overview"
].fillna("")


# =========================================================
# COMBINE ALL FEATURES
# =========================================================

movies["combined_features"] = (

    movies["genres_text"] + " " +

    movies["keywords_text"] + " " +

    movies["cast_text"] + " " +

    movies["director_text"] + " " +

    movies["overview_text"]

)


# =========================================================
# TF-IDF
# =========================================================

print("Creating TF-IDF matrix...")

tfidf = TfidfVectorizer(
    stop_words="english",
    max_features=5000
)


tfidf_matrix = tfidf.fit_transform(
    movies["combined_features"]
)


print(
    "TF-IDF matrix shape:",
    tfidf_matrix.shape
)


# =========================================================
# COSINE SIMILARITY
# =========================================================

print("Calculating cosine similarity...")

cosine_sim = cosine_similarity(
    tfidf_matrix,
    tfidf_matrix
)


print(
    "Cosine similarity matrix:",
    cosine_sim.shape
)


# =========================================================
# MOVIE INDEX
# =========================================================

movie_indices = pd.Series(
    movies.index,
    index=movies["title"].str.lower()
).drop_duplicates()


# =========================================================
# RECOMMENDATION FUNCTION
# =========================================================

def recommend_movies(
    movie_title,
    number_of_movies=5
):

    movie_title = movie_title.lower().strip()

    # Check movie exists
    if movie_title not in movie_indices:

        return []

    # Get movie index
    index = movie_indices[
        movie_title
    ]

    # Get similarity scores
    similarity_scores = list(
        enumerate(
            cosine_sim[index]
        )
    )

    # Sort by similarity
    similarity_scores = sorted(
        similarity_scores,
        key=lambda x: x[1],
        reverse=True
    )

    # Remove selected movie itself
    similarity_scores = similarity_scores[1:]

    # Get top movies
    top_movies = similarity_scores[
        :number_of_movies
    ]

    recommendations = []

    for movie_index, score in top_movies:

        recommendations.append({

            "title":
                movies.iloc[
                    movie_index
                ]["title"],

            "similarity":
                round(
                    float(score),
                    3
                ),

            "rating":
                movies.iloc[
                    movie_index
                ]["vote_average"]

        })

    return recommendations


# =========================================================
# TEST
# =========================================================

if __name__ == "__main__":

    print()
    print("======================================")
    print(" CineAI Recommendation System")
    print("======================================")

    test_movie = "Avatar"

    recommendations = recommend_movies(
        test_movie,
        5
    )

    print()
    print(
        f"Recommendations for: {test_movie}"
    )

    print()

    if recommendations:

        for i, movie in enumerate(
            recommendations,
            start=1
        ):

            print(
                f"{i}. {movie['title']} "
                f"| Similarity: {movie['similarity']} "
                f"| Rating: {movie['rating']}"
            )

    else:

        print(
            "Movie not found."
        )
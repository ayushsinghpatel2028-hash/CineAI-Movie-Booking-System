import pandas as pd
import ast


MOVIES_FILE = "data/tmdb_5000_movies.csv"
CREDITS_FILE = "data/tmdb_5000_credits.csv"


def convert_to_list(text):
    """Convert TMDB JSON-like string into a list of names."""

    try:
        data = ast.literal_eval(text)

        return [
            item["name"]
            for item in data
        ]

    except:
        return []


def get_director(crew):

    try:
        crew_list = ast.literal_eval(crew)

        for person in crew_list:

            if person["job"] == "Director":
                return person["name"]

        return ""

    except:
        return ""


def prepare_movie_data():

    # Load datasets
    movies = pd.read_csv(MOVIES_FILE)
    credits = pd.read_csv(CREDITS_FILE)

    print("Movies loaded:", movies.shape)
    print("Credits loaded:", credits.shape)

    # Rename movie_id
    credits = credits.rename(
        columns={
            "movie_id": "id"
        }
    )

    # Merge movies and credits
    movies = movies.merge(
        credits[
            ["id", "cast", "crew"]
        ],
        on="id",
        how="left"
    )

    # Convert genres
    movies["genres"] = movies["genres"].apply(
        convert_to_list
    )

    # Convert keywords
    movies["keywords"] = movies["keywords"].apply(
        convert_to_list
    )

    # Convert cast
    movies["cast"] = movies["cast"].apply(
        convert_to_list
    )

    # Extract director
    movies["director"] = movies["crew"].apply(
        get_director
    )

    # Keep only useful columns
    movies = movies[
    [
        "id",
        "title",
        "overview",
        "genres",
        "keywords",
        "cast",
        "director",
        "vote_average",
        "vote_count",
        "popularity",
        "release_date"
    ]
]

   
    # Remove movies without title
    movies = movies.dropna(
        subset=["title"]
    )

    # Fill missing values
    movies["overview"] = movies["overview"].fillna("")
    movies["director"] = movies["director"].fillna("")

    # Save cleaned dataset
    movies.to_csv(
        "data/clean_movies.csv",
        index=False
    )

    print("\nCleaned dataset created!")
    print("Total movies:", len(movies))

    return movies


if __name__ == "__main__":

    df = prepare_movie_data()

    print("\nFirst 5 movies:")
    print(
        df[
            [
                "title",
                "genres",
                "director",
                "vote_average"
            ]
        ].head()
    )
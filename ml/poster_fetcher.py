import pandas as pd
import requests
import time
from urllib.parse import quote


# =========================================================
# LOAD MOVIES
# =========================================================

df = pd.read_csv(
    "data/clean_movies.csv"
)


# =========================================================
# POSTER FUNCTION
# =========================================================

def get_poster(title):

    try:

        # Search movie title using OMDb
        url = (
            "https://www.omdbapi.com/"
            "?apikey=YOUR_OMDB_KEY"
            "&t="
            + quote(str(title))
        )

        response = requests.get(
            url,
            timeout=10
        )

        data = response.json()

        poster = data.get(
            "Poster",
            ""
        )

        if poster and poster != "N/A":
            return poster

    except Exception:
        pass

    return ""


# =========================================================
# FETCH POSTERS
# =========================================================

print("Fetching movie posters...")

df["poster_url"] = ""

for index, row in df.iterrows():

    title = row["title"]

    poster = get_poster(title)

    df.at[
        index,
        "poster_url"
    ] = poster

    print(
        f"{index + 1}/{len(df)} - {title}"
    )

    time.sleep(0.1)


# =========================================================
# SAVE
# =========================================================

df.to_csv(
    "data/clean_movies.csv",
    index=False
)

print()
print("===================================")
print("POSTERS ADDED SUCCESSFULLY")
print("===================================")
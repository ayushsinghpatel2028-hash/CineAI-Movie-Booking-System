import pandas as pd
import requests
import time
import os

CSV_PATH = "data/clean_movies_with_posters.csv"

API_URL = "https://www.omdbapi.com/"
API_KEY = "564727fa"

# Load existing poster file
df = pd.read_csv(CSV_PATH)

# Make sure column exists
if "poster_url" not in df.columns:
    df["poster_url"] = ""

total = len(df)

print("=" * 50)
print("CineAI Poster Downloader")
print("=" * 50)
print(f"Total movies: {total}")

found = 0
not_found = 0

for index, row in df.iterrows():

    title = str(row["title"]).strip()

    # Skip movies that already have a poster
    existing = row["poster_url"]

    if pd.notna(existing) and str(existing).strip():
        continue

    try:

        params = {
            "t": title,
            "apikey": API_KEY
        }

        response = requests.get(
            API_URL,
            params=params,
            timeout=10
        )

        data = response.json()

        if data.get("Response") == "True":

            poster = data.get("Poster")

            if poster and poster != "N/A":

                df.at[index, "poster_url"] = poster

                found += 1

                print(
                    f"✅ {index + 1}/{total} - {title}"
                )

            else:

                not_found += 1

                print(
                    f"⚠️ No poster - {title}"
                )

        else:

            not_found += 1

            print(
                f"❌ Not found - {title}"
            )

    except Exception as e:

        print(
            f"❌ Error - {title}: {e}"
        )

    # Save progress every 25 movies
    if (index + 1) % 25 == 0:

        df.to_csv(
            CSV_PATH,
            index=False
        )

        print("\n💾 Progress saved...\n")

    time.sleep(0.25)


# Final save
df.to_csv(
    CSV_PATH,
    index=False
)

print("\n" + "=" * 50)
print("POSTER DOWNLOAD FINISHED")
print("=" * 50)

poster_count = (
    df["poster_url"]
    .fillna("")
    .astype(str)
    .str.strip()
    .ne("")
    .sum()
)

print(f"Posters available: {poster_count}/{total}")
print(f"Posters missing: {total - poster_count}")
import streamlit as st
import pandas as pd
import requests
import sys
import os

PROJECT_ROOT = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

sys.path.append(PROJECT_ROOT)
from ml.demand_prediction import predict_demand

from ml.recommendation import recommend_movies

API_URL = "http://127.0.0.1:8000"
# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="CineAI",
    page_icon="🎬",
    layout="wide"
)

# =========================================================
# LOAD DATA
# =========================================================

@st.cache_data
def load_movies():
    try:
        # Use the poster-enabled movie dataset
        movies_path = os.path.join(
            PROJECT_ROOT,
            "data",
            "clean_movies_with_posters.csv"
        )
        return pd.read_csv(movies_path)

    except FileNotFoundError:
        st.error(
            "data/clean_movies_with_posters.csv not found. "
            "Run poster_downloader.py first."
        )
        st.stop()


movies = load_movies()

# =========================================================
# CSS + HERO
# =========================================================

st.html("""
<style>

body {
    background-color: #050505;
}

/* MAIN CONTAINER */

.cine-container {
    width: 100%;
    font-family: Arial, sans-serif;
}

/* LOGO */

.logo {
    font-size: 44px;
    font-weight: 900;
    margin-bottom: 25px;
    color: white;
    letter-spacing: -1px;
}

.logo-red {
    color: #E50914;
}

/* HERO */

.hero {
    width: 100%;
    min-height: 470px;

    border-radius: 24px;

    background:
        radial-gradient(
            circle at 80% 30%,
            rgba(229, 9, 20, 0.25),
            transparent 35%
        ),
        linear-gradient(
            110deg,
            #050505 0%,
            #111111 55%,
            #1b0809 100%
        );

    border: 1px solid #292929;

    display: flex;
    align-items: center;

    padding: 65px;

    box-sizing: border-box;

    position: relative;
    overflow: hidden;
}

/* RED GLOW */

.hero::after {
    content: "";

    position: absolute;

    width: 320px;
    height: 320px;

    right: -100px;
    bottom: -140px;

    background: rgba(229, 9, 20, 0.18);

    filter: blur(80px);

    border-radius: 50%;
}

/* HERO CONTENT */

.hero-content {
    max-width: 700px;
    position: relative;
    z-index: 2;
}

/* SMALL LABEL */

.hero-label {
    display: inline-block;

    color: #E50914;

    font-size: 14px;
    font-weight: 800;

    letter-spacing: 2px;

    margin-bottom: 15px;
}

/* TITLE */

.hero-title {
    color: white;

    font-size: 60px;

    font-weight: 900;

    line-height: 1.05;

    letter-spacing: -2px;
}

/* DESCRIPTION */

.hero-description {
    color: #cfcfcf;

    font-size: 18px;

    line-height: 1.7;

    margin-top: 22px;

    max-width: 620px;
}

/* INFO */

.hero-info {
    color: #bdbdbd;

    font-size: 15px;

    margin-top: 22px;

    line-height: 1.8;
}

/* BUTTON */

.hero-button {
    display: inline-block;

    margin-top: 28px;

    background: #E50914;

    color: white;

    padding: 14px 28px;

    border-radius: 8px;

    font-weight: 800;

    font-size: 16px;

    box-shadow:
        0 8px 25px rgba(229, 9, 20, 0.25);
}

/* AI BADGE */

.ai-badge {
    display: inline-block;

    margin-left: 10px;

    padding: 7px 12px;

    border-radius: 20px;

    background: rgba(255,255,255,0.07);

    border: 1px solid #333;

    color: #ddd;

    font-size: 13px;
}

/* SECTION */

.section-title {
    color: white;

    font-size: 28px;

    font-weight: 800;

    margin-top: 35px;

    margin-bottom: 15px;
}

</style>


<div class="cine-container">

    <div class="logo">
        🎬 Cine<span class="logo-red">AI</span>
    </div>


    <div class="hero">

        <div class="hero-content">

            <div class="hero-label">
                ✦ AI POWERED CINEMA EXPERIENCE
            </div>

            <div class="hero-title">
                Your Movie<br>
                Universe 🎬
            </div>

            <div class="hero-description">
                Discover movies you love, get personalized
                AI recommendations and book your perfect
                cinema seats — all in one place.
            </div>

            <div class="hero-info">
                ⭐ AI Powered
                &nbsp;&nbsp; | &nbsp;&nbsp;

                🎬 Smart Recommendations
                &nbsp;&nbsp; | &nbsp;&nbsp;

                🎟️ Easy Booking
            </div>

            <div class="hero-button">
                ▶ Explore Movies
            </div>

            <span class="ai-badge">
                🤖 XGBoost Demand AI
            </span>

        </div>

    </div>

</div>
""")

# =========================================================
# SEARCH
# =========================================================

st.html("""
<div class="section-title">
    🔍 Find Your Movie
</div>
""")

search = st.text_input(
    "Search",
    placeholder="Search for a movie...",
    label_visibility="collapsed"
)

# Filter movies

if search.strip():

    filtered_movies = movies[
        movies["title"]
        .astype(str)
        .str.contains(
            search,
            case=False,
            na=False
        )
    ]

else:

    filtered_movies = movies


# =========================================================
# MOVIE SECTION + HORIZONTAL SLIDER
# =========================================================

def movie_section(title, dataframe, limit=10):

    st.html(f"""
    <div class="section-title">
        {title}
    </div>
    """)

    dataframe = dataframe.head(limit)

    if dataframe.empty:
        st.info("No movies found.")
        return

    cards = []

    for _, movie in dataframe.iterrows():

        movie_title = str(movie.get("title", "Unknown Movie"))

        try:
            rating = float(movie.get("vote_average", 0))
        except (TypeError, ValueError):
            rating = 0

        poster = movie.get("poster_url", "")

        if pd.isna(poster):
            poster = ""

        safe_title = (
            movie_title
            .replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace('"', "&quot;")
        )

        if poster:
            safe_poster = str(poster).replace('"', "&quot;")

            image_html = f"""
                <div class="poster-wrapper">
                    <img src="{safe_poster}"
                         alt="{safe_title}"
                         class="movie-poster">
                    <div class="poster-overlay">
                        <span>▶</span>
                    </div>
                </div>
            """
        else:
            image_html = """
                <div class="poster-wrapper">
                    <div class="movie-placeholder">
                        🎬
                    </div>
                </div>
            """

        cards.append(f"""
            <div class="movie-card">

                {image_html}

                <div class="movie-card-info">

                    <div class="movie-card-title">
                        {safe_title}
                    </div>

                    <div class="movie-card-bottom">

                        <div class="movie-card-rating">
                            ⭐ {rating:.1f}
                        </div>

                        <div class="movie-card-type">
                            MOVIE
                        </div>

                    </div>

                </div>

            </div>
        """)

    cards_html = "\n".join(cards)

    st.html(f"""
    <style>

    /* ================================
       MOVIE HORIZONTAL SLIDER
       ================================ */

    .movie-slider {{
        display:flex;
        gap:20px;
        overflow-x:auto;
        overflow-y:hidden;
        scroll-behavior:smooth;
        padding:10px 5px 25px 5px;
    }}

    .movie-slider::-webkit-scrollbar {{
        height:7px;
    }}

    .movie-slider::-webkit-scrollbar-track {{
        background:#111;
        border-radius:10px;
    }}

    .movie-slider::-webkit-scrollbar-thumb {{
        background:#444;
        border-radius:10px;
    }}

    .movie-slider::-webkit-scrollbar-thumb:hover {{
        background:#E50914;
    }}

    /* ================================
       MOVIE CARD
       ================================ */

    .movie-card {{
        flex:0 0 210px;
        width:210px;

        background:#151515;

        border:1px solid #292929;
        border-radius:14px;

        overflow:hidden;

        transition:
            transform .25s ease,
            border-color .25s ease,
            box-shadow .25s ease;

        cursor:pointer;
    }}

    .movie-card:hover {{
        transform:translateY(-8px) scale(1.03);

        border-color:#E50914;

        box-shadow:
            0 15px 35px rgba(0,0,0,.65);
    }}

    /* ================================
       POSTER
       ================================ */

    .poster-wrapper {{
        position:relative;
        width:100%;
        height:300px;
        overflow:hidden;
        background:#111;
    }}

    .movie-poster {{
        width:100%;
        height:300px;

        object-fit:cover;

        display:block;

        transition:transform .35s ease;
    }}

    .movie-card:hover .movie-poster {{
        transform:scale(1.08);
    }}

    /* ================================
       HOVER OVERLAY
       ================================ */

    .poster-overlay {{
        position:absolute;

        inset:0;

        display:flex;
        align-items:center;
        justify-content:center;

        background:rgba(0,0,0,.35);

        opacity:0;

        transition:opacity .25s ease;
    }}

    .movie-card:hover .poster-overlay {{
        opacity:1;
    }}

    .poster-overlay span {{
        width:48px;
        height:48px;

        border-radius:50%;

        background:#E50914;

        color:white;

        display:flex;
        align-items:center;
        justify-content:center;

        font-size:20px;

        padding-left:3px;

        box-shadow:0 5px 20px rgba(0,0,0,.5);
    }}

    /* ================================
       PLACEHOLDER
       ================================ */

    .movie-placeholder {{
        width:100%;
        height:300px;

        background:
            linear-gradient(
                145deg,
                #292929,
                #101010
            );

        display:flex;
        align-items:center;
        justify-content:center;

        font-size:65px;
    }}

    /* ================================
       CARD INFORMATION
       ================================ */

    .movie-card-info {{
        padding:13px 14px 15px;
    }}

    .movie-card-title {{
        color:white;

        font-size:16px;
        font-weight:700;

        line-height:1.35;

        min-height:43px;

        display:-webkit-box;
        -webkit-line-clamp:2;
        -webkit-box-orient:vertical;

        overflow:hidden;
    }}

    .movie-card-bottom {{
        display:flex;

        justify-content:space-between;
        align-items:center;

        margin-top:9px;
    }}

    .movie-card-rating {{
        color:#f5c518;

        font-size:14px;
        font-weight:700;
    }}

    .movie-card-type {{
        color:#888;

        font-size:10px;

        font-weight:700;

        letter-spacing:1px;
    }}

    </style>

    <div class="movie-slider">
        {cards_html}
    </div>
    """)

# =========================================================
# TRENDING
# =========================================================

trending = movies.sort_values(
    "popularity",
    ascending=False
)

movie_section(
    "🔥 Trending Now",
    trending,
    limit=10
)
# =========================================================
# MOVIE DETAILS
# =========================================================

st.markdown("---")

st.html("""
<div style="
    font-size:32px;
    font-weight:900;
    color:white;
    margin-top:40px;
">
    🎬 Explore Movie Details
</div>
""")

# Get movies from database/API

try:

    detail_response = requests.get(
        f"{API_URL}/movies",
        timeout=5
    )

    detail_response.raise_for_status()

    detail_movies = detail_response.json()

except Exception:

    st.warning(
        "Unable to load movie details."
    )

    detail_movies = []


if detail_movies:

    movie_titles = [
        movie["title"]
        for movie in detail_movies
    ]

    selected_detail_movie = st.selectbox(
        "🎬 Choose a movie to explore",
        movie_titles,
        key="movie_details_selector"
    )

    movie_data = next(
        movie
        for movie in detail_movies
        if movie["title"] == selected_detail_movie
    )

    col1, col2 = st.columns(
        [1, 2]
    )

    with col1:

        st.html("""
        <div style="
            height:380px;
            background:linear-gradient(
                145deg,
                #242424,
                #111
            );
            border-radius:18px;
            display:flex;
            align-items:center;
            justify-content:center;
            font-size:90px;
            border:1px solid #333;
        ">
            🎬
        </div>
        """)

    with col2:

        st.markdown(
            f"""
            # {movie_data["title"]}

            ⭐ **{movie_data["rating"]}/10**

            🎭 **Genre:**  
            {movie_data["genre"]}

            """
        )

        st.markdown(
            """
            ### 🍿 Why watch this?

            Enjoy this movie on the big screen with
            comfortable seating and easy online booking.
            """
        )

        if st.button(
            "🎟️ Book This Movie",
            type="primary",
            key="detail_book_button"
        ):

            st.session_state[
                "booking_movie"
            ] = movie_data["title"]

            st.success(
                f"Selected: {movie_data['title']}"
            )

            st.info(
                "Scroll down to the booking section "
                "to select your theatre, show and seats."
            )


# =========================================================
# TOP RATED
# =========================================================

top_rated = movies.sort_values(
    "vote_average",
    ascending=False
)

movie_section(
    "⭐ Top Rated",
    top_rated
)


# =========================================================
# ACTION
# =========================================================

action_movies = movies[
    movies["genres"]
    .astype(str)
    .str.contains(
        "Action",
        case=False,
        na=False
    )
]

movie_section(
    "💥 Action Movies",
    action_movies
)


# =========================================================
# SCIENCE FICTION
# =========================================================

scifi_movies = movies[
    movies["genres"]
    .astype(str)
    .str.contains(
        "Science Fiction",
        case=False,
        na=False
    )
]

movie_section(
    "🚀 Science Fiction",
    scifi_movies
)


# =========================================================
# AI RECOMMENDATION
# =========================================================

st.html("""
<div class="section-title">
    🤖 AI Picks For You
</div>
""")

st.info(
    "TF-IDF + Cosine Similarity recommendation "
    "system will be added next."
)


# =========================================================
# FOOTER
# =========================================================

# =========================================================
# AI RECOMMENDATION SYSTEM
# =========================================================

st.html("""
<div class="section-title">
    🤖 AI Movie Recommendations
</div>
""")

st.write(
    "Select a movie and CineAI will find similar movies "
    "using TF-IDF and Cosine Similarity."
)

# Movie selector

movie_list = sorted(
    movies["title"]
    .dropna()
    .unique()
    .tolist()
)

selected_movie = st.selectbox(
    "Choose a movie",
    movie_list
)

# Recommendation button

if st.button(
    "🤖 Get AI Recommendations"
):

    recommendations = recommend_movies(
        selected_movie,
        6
    )

    if recommendations:

        st.success(
            f"Recommendations based on: {selected_movie}"
        )

        columns = st.columns(
            len(recommendations)
        )

        for i, movie in enumerate(
            recommendations
        ):

            with columns[i]:

                st.html(
                    f"""
                    <div style="
                        background:#151515;
                        border-radius:12px;
                        padding:15px;
                        border:1px solid #292929;
                        min-height:140px;
                    ">

                        <div style="
                            color:white;
                            font-size:16px;
                            font-weight:bold;
                        ">
                            🎬 {movie["title"]}
                        </div>

                        <div style="
                            color:#f5c518;
                            margin-top:10px;
                        ">
                            ⭐ Rating:
                            {float(movie["rating"]):.1f}
                        </div>

                        <div style="
                            color:#4CAF50;
                            margin-top:8px;
                        ">
                            🤖 Similarity:
                            {float(movie["similarity"]) * 100:.1f}%
                        </div>

                    </div>
                    """
                )

    else:

        st.warning(
            "Movie not found in the recommendation system."
        )
        # =========================================================
# MOVIE TICKET BOOKING
# =========================================================

# =========================================================
# MOVIE TICKET BOOKING
# =========================================================

st.html("""
<style>

.booking-title {
    font-size: 32px;
    font-weight: 900;
    color: white;
    margin-top: 50px;
    margin-bottom: 10px;
}

.booking-subtitle {
    color: #999;
    font-size: 16px;
    margin-bottom: 25px;
}

.screen {
    background: linear-gradient(
        90deg,
        transparent,
        #eeeeee,
        transparent
    );

    height: 5px;
    border-radius: 50%;

    margin: 20px auto 35px auto;

    width: 70%;

    box-shadow: 0 0 20px #ffffff;
}

.legend {
    text-align: center;
    margin: 25px 0;
    color: #bbbbbb;
}

.confirmation {
    background: #151515;
    border: 1px solid #333;
    border-radius: 15px;
    padding: 25px;
    margin-top: 25px;
}

</style>

<div class="booking-title">
    🎟️ Book Your Movie Tickets
</div>

<div class="booking-subtitle">
    Select your movie, theatre, show and preferred seats.
</div>
""")

# =========================================================
# GET MOVIES
# =========================================================

try:

    movie_response = requests.get(
        f"{API_URL}/movies",
        timeout=5
    )

    movie_response.raise_for_status()

    api_movies = movie_response.json()

except Exception:

    st.error(
        "❌ FastAPI is not running. "
        "Start it using: uvicorn backend.main:app --reload"
    )

    st.stop()


# =========================================================
# MOVIE
# =========================================================

movie_names = [
    movie["title"]
    for movie in api_movies
]

selected_movie_name = st.selectbox(
    "🎬 Select Movie",
    movie_names
)

selected_movie = next(
    movie
    for movie in api_movies
    if movie["title"] == selected_movie_name
)

movie_id = selected_movie["id"]


# =========================================================
# THEATRES
# =========================================================

try:

    theatre_response = requests.get(
        f"{API_URL}/theatres",
        timeout=5
    )

    theatre_response.raise_for_status()

    theatres = theatre_response.json()

except Exception:

    st.error("❌ Unable to load theatres.")

    st.stop()


theatre_names = [
    theatre["name"]
    for theatre in theatres
]

selected_theatre_name = st.selectbox(
    "🏢 Select Theatre",
    theatre_names
)

selected_theatre = next(
    theatre
    for theatre in theatres
    if theatre["name"] == selected_theatre_name
)

theatre_id = selected_theatre["id"]


# =========================================================
# SHOWS
# =========================================================

try:

    show_response = requests.get(
        f"{API_URL}/movies/{movie_id}/shows",
        timeout=5
    )

    show_response.raise_for_status()

    all_shows = show_response.json()

except Exception:

    st.error("❌ Unable to load shows.")

    st.stop()


theatre_shows = [

    show

    for show in all_shows

    if show["theatre_id"] == theatre_id

]


if not theatre_shows:

    st.warning(
        "No shows available for this movie and theatre."
    )

    st.stop()


# =========================================================
# SHOW SELECTOR
# =========================================================

show_options = {

    f"{show['show_date']} | "
    f"{show['show_time']} | "
    f"₹{show['price']}":

        show["id"]

    for show in theatre_shows

}


selected_show_text = st.selectbox(
    "🕐 Select Show",
    list(show_options.keys())
)


selected_show_id = show_options[
    selected_show_text
]


selected_show = next(
    show
    for show in theatre_shows
    if show["id"] == selected_show_id
)


ticket_price = float(
    selected_show["price"]
)


# =========================================================
# RESET SELECTED SEATS WHEN SHOW CHANGES
# =========================================================

if (
    "active_show" not in st.session_state
    or
    st.session_state.active_show
    != selected_show_id
):

    st.session_state.active_show = (
        selected_show_id
    )

    st.session_state.selected_seats = []


if "selected_seats" not in st.session_state:

    st.session_state.selected_seats = []


# =========================================================
# GET SEATS
# =========================================================

try:

    seat_response = requests.get(
        f"{API_URL}/shows/{selected_show_id}/seats",
        timeout=5
    )

    seat_response.raise_for_status()

    seats = seat_response.json()

except Exception:

    st.error("❌ Unable to load seats.")

    st.stop()


# =========================================================
# AI DEMAND PREDICTION
# =========================================================

try:

    show_date = pd.to_datetime(
        selected_show["show_date"],
        errors="coerce"
    )

    if pd.isna(show_date):
        day_of_week = 5
    else:
        day_of_week = show_date.weekday()

    is_weekend = 1 if day_of_week >= 5 else 0

    show_time = str(
        selected_show["show_time"]
    )

    try:
        show_hour = int(
            show_time.split(":")[0]
        )
    except Exception:
        show_hour = 20

    movie_rating = float(
        selected_movie.get("rating", 7.5)
    )

    previous_bookings = sum(
        1
        for seat in seats
        if seat["status"] == "booked"
    )

    predicted_demand = predict_demand(
        day_of_week=day_of_week,
        show_hour=show_hour,
        is_weekend=is_weekend,
        movie_rating=movie_rating,
        ticket_price=ticket_price,
        previous_bookings=previous_bookings
    )

    if predicted_demand >= 70:
        demand_level = "HIGH 🔥"
        demand_message = (
            "This show is expected to have high demand."
        )

    elif predicted_demand >= 40:
        demand_level = "MEDIUM 🟡"
        demand_message = (
            "This show is expected to have moderate demand."
        )

    else:
        demand_level = "LOW 🟢"
        demand_message = (
            "This show is expected to have lower demand."
        )

    st.markdown("### 🤖 AI Demand Prediction")

    st.html(
        f"""
        <div style="
            background:linear-gradient(
                135deg,
                #191919,
                #101010
            );
            border:1px solid #333;
            border-radius:18px;
            padding:25px;
            margin:15px 0 25px 0;
        ">

            <div style="
                color:#aaa;
                font-size:14px;
            ">
                XGBoost Prediction
            </div>

            <div style="
                color:white;
                font-size:32px;
                font-weight:800;
                margin-top:5px;
            ">
                {predicted_demand:.0f}%
            </div>

            <div style="
                color:#FFD700;
                font-size:20px;
                font-weight:700;
                margin-top:5px;
            ">
                {demand_level}
            </div>

            <div style="
                color:#aaa;
                margin-top:10px;
            ">
                {demand_message}
            </div>

        </div>
        """
    )

except Exception as e:

    st.warning(
        f"AI demand prediction unavailable: {e}"
    )


# =========================================================
# CINEMA INFORMATION
# =========================================================

# =========================================================
# CINEMA INFORMATION
# =========================================================

st.html(
    f"""
    <div style="
        background:#151515;
        padding:20px;
        border-radius:15px;
        border:1px solid #292929;
        margin-top:20px;
    ">

        <div style="
            color:white;
            font-size:22px;
            font-weight:bold;
        ">
            🎬 {selected_movie_name}
        </div>

        <div style="
            color:#aaa;
            margin-top:8px;
        ">
            🏢 {selected_theatre_name}
            &nbsp;&nbsp; | &nbsp;&nbsp;
            🕐 {selected_show_text}
        </div>

    </div>
    """
)


# =========================================================
# SCREEN
# =========================================================

st.html("""
<div style="
    text-align:center;
    color:#999;
    margin-top:35px;
    font-size:13px;
">
    SCREEN
</div>

<div class="screen"></div>
""")


# =========================================================
# SEAT LEGEND
# =========================================================

st.markdown(
    """
    <div class="legend">
        🟢 Available &nbsp;&nbsp;
        🔵 Selected &nbsp;&nbsp;
        🔴 Booked
    </div>
    """,
    unsafe_allow_html=True
)


# =========================================================
# SEAT GRID
# =========================================================

rows = ["A", "B", "C", "D", "E"]

for row in rows:

    row_seats = [

        seat

        for seat in seats

        if seat["seat_number"].startswith(row)

    ]

    columns = st.columns(8)

    for i, seat in enumerate(row_seats):

        seat_number = seat["seat_number"]

        status = seat["status"]

        with columns[i]:

            # -----------------------------------------
            # BOOKED
            # -----------------------------------------

            if status == "booked":

                st.button(
                    f"🔴 {seat_number}",
                    disabled=True,
                    key=(
                        f"booked_"
                        f"{selected_show_id}_"
                        f"{seat_number}"
                    )
                )

            # -----------------------------------------
            # AVAILABLE / SELECTED
            # -----------------------------------------

            else:

                if seat_number in st.session_state.selected_seats:

                    label = f"🔵 {seat_number}"

                else:

                    label = f"🟢 {seat_number}"


                clicked = st.button(
                    label,
                    key=(
                        f"seat_"
                        f"{selected_show_id}_"
                        f"{seat_number}"
                    )
                )


                if clicked:

                    if (
                        seat_number
                        in st.session_state.selected_seats
                    ):

                        st.session_state.selected_seats.remove(
                            seat_number
                        )

                    else:

                        st.session_state.selected_seats.append(
                            seat_number
                        )

                    st.rerun()


# =========================================================
# BOOKING SUMMARY
# =========================================================

st.markdown("---")

st.subheader("🧾 Booking Summary")


selected_seats = (
    st.session_state.selected_seats
)


number_of_seats = len(
    selected_seats
)


total_amount = (
    number_of_seats
    * ticket_price
)


if selected_seats:

    st.success(
        "Selected Seats: "
        + ", ".join(selected_seats)
    )

else:

    st.info(
        "No seats selected."
    )


col1, col2, col3 = st.columns(3)


with col1:

    st.metric(
        "Seats",
        number_of_seats
    )


with col2:

    st.metric(
        "Price / Seat",
        f"₹{ticket_price:.0f}"
    )


with col3:

    st.metric(
        "Total",
        f"₹{total_amount:.0f}"
    )


# =========================================================
# CUSTOMER DETAILS
# =========================================================

st.markdown("### 👤 Customer Details")


customer_name = st.text_input(
    "Name",
    placeholder="Enter your name"
)


customer_email = st.text_input(
    "Email",
    placeholder="Enter your email"
)


# =========================================================
# CONFIRM BOOKING
# =========================================================

if st.button(
    "🎟️ Confirm Booking",
    type="primary",
    use_container_width=True
):

    # ---------------------------------------------
    # VALIDATION
    # ---------------------------------------------

    if not selected_seats:

        st.warning(
            "⚠️ Please select at least one seat."
        )

    elif not customer_name.strip():

        st.warning(
            "⚠️ Please enter your name."
        )

    elif not customer_email.strip():

        st.warning(
            "⚠️ Please enter your email."
        )

    else:

        booking_data = {

            "customer_name":
                customer_name,

            "customer_email":
                customer_email,

            "show_id":
                selected_show_id,

            "seat_numbers":
                selected_seats

        }


        # -----------------------------------------
        # SEND TO FASTAPI
        # -----------------------------------------

        try:

            response = requests.post(

                f"{API_URL}/bookings",

                json=booking_data,

                timeout=5

            )


            # -------------------------------------
            # SUCCESS
            # -------------------------------------

            if response.status_code == 200:

                result = response.json()


                st.balloons()


                st.success(
                    "🎉 Booking Confirmed Successfully!"
                )


                st.html(
                    f"""
                    <div class="confirmation">

                        <div style="
                            color:#E50914;
                            font-size:25px;
                            font-weight:bold;
                        ">
                            🎟️ CineAI Booking
                        </div>

                        <br>

                        <div style="color:white;">
                            <b>Booking ID:</b>
                            {result["booking_id"]}
                        </div>

                        <div style="color:white;">
                            <b>Movie:</b>
                            {selected_movie_name}
                        </div>

                        <div style="color:white;">
                            <b>Theatre:</b>
                            {selected_theatre_name}
                        </div>

                        <div style="color:white;">
                            <b>Show:</b>
                            {selected_show_text}
                        </div>

                        <div style="color:white;">
                            <b>Seats:</b>
                            {", ".join(selected_seats)}
                        </div>

                        <div style="
                            color:#f5c518;
                            font-size:20px;
                            margin-top:10px;
                        ">
                            <b>Total:</b>
                            ₹{result["total_amount"]}
                        </div>

                    </div>
                    """
                )


                # Clear selected seats

                st.session_state.selected_seats = []


            # -------------------------------------
            # ERROR
            # -------------------------------------

            else:

                error_data = response.json()

                st.error(
                    f"❌ Booking failed: "
                    f"{error_data.get('detail')}"
                )


        except Exception as error:

            st.error(
                f"❌ Could not connect to FastAPI: {error}"
            )
            # =========================================================
# MY BOOKINGS
# =========================================================

st.markdown("---")

st.html("""
<div style="
    font-size:32px;
    font-weight:900;
    color:white;
    margin-top:40px;
">
    🎟️ My Bookings
</div>

<div style="
    color:#999;
    margin-bottom:20px;
">
    Enter your email to view your CineAI booking history.
</div>
""")


booking_email = st.text_input(
    "📧 Booking Email",
    placeholder="Enter the email used for booking"
)


if st.button(
    "🔍 Find My Bookings",
    use_container_width=True
):

    if not booking_email.strip():

        st.warning(
            "Please enter your email."
        )

    else:

        try:

            booking_response = requests.get(
                f"{API_URL}/bookings",
                params={
                    "email": booking_email
                },
                timeout=5
            )

            booking_response.raise_for_status()

            bookings = booking_response.json()


            if not bookings:

                st.info(
                    "No bookings found for this email."
                )

            else:

                st.success(
                    f"Found {len(bookings)} booking(s)."
                )


                for booking in bookings:

                    st.html(
                        f"""
                        <div style="
                            background:#151515;
                            border:1px solid #333;
                            border-radius:18px;
                            padding:25px;
                            margin:15px 0;
                        ">

                            <div style="
                                display:flex;
                                justify-content:space-between;
                                align-items:center;
                            ">

                                <div style="
                                    color:#E50914;
                                    font-size:22px;
                                    font-weight:bold;
                                ">
                                    🎟️ Booking #
                                    {booking["booking_id"]}
                                </div>

                                <div style="
                                    color:#4CAF50;
                                    font-weight:bold;
                                ">
                                    ● CONFIRMED
                                </div>

                            </div>

                            <hr style="
                                border-color:#333;
                            ">

                            <div style="
                                color:white;
                                font-size:20px;
                                font-weight:bold;
                            ">
                                🎬 {booking["movie"]}
                            </div>

                            <div style="
                                color:#aaa;
                                margin-top:10px;
                            ">
                                🏢 {booking["theatre"]}
                                <br>

                                📍 {booking["location"]}
                                <br>

                                📅 {booking["show_date"]}
                                <br>

                                🕐 {booking["show_time"]}
                            </div>

                            <div style="
                                color:#ddd;
                                margin-top:15px;
                            ">
                                💺 Seats:
                                <b>
                                    {booking["seats"]}
                                </b>
                            </div>

                            <div style="
                                color:#f5c518;
                                font-size:22px;
                                font-weight:bold;
                                margin-top:15px;
                            ">
                                💰 ₹{booking["total_amount"]}
                            </div>

                        </div>
                        """
                    )


        except Exception as error:

            st.error(
                f"Unable to retrieve bookings: {error}"
            )
            
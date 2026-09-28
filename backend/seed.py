from datetime import date, time

from backend.database import SessionLocal

from backend.models import (
    Movie,
    Theatre,
    Show,
    Seat
)


# =========================================================
# DATABASE
# =========================================================

db = SessionLocal()


# =========================================================
# CLEAR OLD DATA
# =========================================================

db.query(Seat).delete()
db.query(Show).delete()
db.query(Theatre).delete()
db.query(Movie).delete()

db.commit()


# =========================================================
# MOVIES
# =========================================================

movies = [

    Movie(
        title="Avatar",
        genre="Action, Adventure, Science Fiction",
        rating=7.2
    ),

    Movie(
        title="The Dark Knight",
        genre="Action, Crime, Drama",
        rating=7.6
    ),

    Movie(
        title="Interstellar",
        genre="Adventure, Drama, Science Fiction",
        rating=8.6
    ),

    Movie(
        title="Inception",
        genre="Action, Science Fiction, Thriller",
        rating=8.4
    ),

    Movie(
        title="Avengers: Endgame",
        genre="Action, Adventure, Science Fiction",
        rating=8.3
    )
]


db.add_all(movies)

db.commit()


# =========================================================
# THEATRES
# =========================================================

theatres = [

    Theatre(
        name="Cinepolis",
        location="Greater Noida"
    ),

    Theatre(
        name="PVR Cinemas",
        location="Greater Noida"
    ),

    Theatre(
        name="INOX",
        location="Noida"
    )
]


db.add_all(theatres)

db.commit()


# =========================================================
# SHOWS
# =========================================================

shows = [

    Show(
        movie_id=movies[0].id,
        theatre_id=theatres[0].id,
        show_date=date(2026, 9, 29),
        show_time=time(18, 30),
        price=250
    ),

    Show(
        movie_id=movies[0].id,
        theatre_id=theatres[1].id,
        show_date=date(2026, 9, 29),
        show_time=time(21, 30),
        price=300
    ),

    Show(
        movie_id=movies[1].id,
        theatre_id=theatres[0].id,
        show_date=date(2026, 9, 29),
        show_time=time(19, 00),
        price=280
    ),

    Show(
        movie_id=movies[2].id,
        theatre_id=theatres[1].id,
        show_date=date(2026, 9, 29),
        show_time=time(20, 00),
        price=300
    ),

    Show(
        movie_id=movies[3].id,
        theatre_id=theatres[2].id,
        show_date=date(2026, 9, 29),
        show_time=time(18, 00),
        price=220
    )
]


db.add_all(shows)

db.commit()


# =========================================================
# CREATE SEATS
# =========================================================

rows = [
    "A",
    "B",
    "C",
    "D",
    "E"
]

seat_numbers = []

for row in rows:

    for number in range(1, 9):

        seat_numbers.append(
            f"{row}{number}"
        )


for show in shows:

    for seat_number in seat_numbers:

        seat = Seat(
            show_id=show.id,
            seat_number=seat_number,
            status="available"
        )

        db.add(seat)


db.commit()


print()
print("================================")
print("CINEAI DATABASE SEEDED")
print("================================")
print("Movies:", len(movies))
print("Theatres:", len(theatres))
print("Shows:", len(shows))
print("Seats created:", len(shows) * len(seat_numbers))
print("================================")


db.close()
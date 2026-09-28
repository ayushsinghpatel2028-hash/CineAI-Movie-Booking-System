from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel

from backend.database import engine, Base, SessionLocal
from backend import models


# =========================================================
# CREATE DATABASE TABLES
# =========================================================

Base.metadata.create_all(bind=engine)


# =========================================================
# FASTAPI APP
# =========================================================

app = FastAPI(
    title="CineAI API",
    description="AI Powered Movie Booking System",
    version="1.0"
)


# =========================================================
# DATABASE CONNECTION
# =========================================================

def get_db():

    db = SessionLocal()

    try:
        yield db

    finally:
        db.close()


# =========================================================
# BOOKING REQUEST SCHEMA
# =========================================================

class BookingRequest(BaseModel):

    customer_name: str
    customer_email: str
    show_id: int
    seat_numbers: list[str]


# =========================================================
# HOME
# =========================================================

@app.get("/")
def home():

    return {
        "message": "Welcome to CineAI API",
        "status": "running"
    }


# =========================================================
# HEALTH
# =========================================================

@app.get("/health")
def health():

    return {
        "status": "healthy"
    }


# =========================================================
# GET MOVIES
# =========================================================

@app.get("/movies")
def get_movies(
    db: Session = Depends(get_db)
):

    return db.query(
        models.Movie
    ).all()


# =========================================================
# GET THEATRES
# =========================================================

@app.get("/theatres")
def get_theatres(
    db: Session = Depends(get_db)
):

    return db.query(
        models.Theatre
    ).all()


# =========================================================
# GET SHOWS
# =========================================================

@app.get("/shows")
def get_shows(
    db: Session = Depends(get_db)
):

    return db.query(
        models.Show
    ).all()


# =========================================================
# GET SHOWS FOR A MOVIE
# =========================================================

@app.get("/movies/{movie_id}/shows")
def get_movie_shows(
    movie_id: int,
    db: Session = Depends(get_db)
):

    shows = db.query(
        models.Show
    ).filter(
        models.Show.movie_id == movie_id
    ).all()

    if not shows:

        raise HTTPException(
            status_code=404,
            detail="No shows found for this movie"
        )

    return shows


# =========================================================
# GET SEATS FOR A SHOW
# =========================================================

@app.get("/shows/{show_id}/seats")
def get_show_seats(
    show_id: int,
    db: Session = Depends(get_db)
):

    seats = db.query(
        models.Seat
    ).filter(
        models.Seat.show_id == show_id
    ).all()

    if not seats:

        raise HTTPException(
            status_code=404,
            detail="No seats found for this show"
        )

    return seats


# =========================================================
# BOOK SEATS
# =========================================================

@app.post("/bookings")
def create_booking(
    booking: BookingRequest,
    db: Session = Depends(get_db)
):

    # ---------------------------------------------
    # CHECK SHOW
    # ---------------------------------------------

    show = db.query(
        models.Show
    ).filter(
        models.Show.id == booking.show_id
    ).first()

    if not show:

        raise HTTPException(
            status_code=404,
            detail="Show not found"
        )


    # ---------------------------------------------
    # CHECK SEATS
    # ---------------------------------------------

    seats = db.query(
        models.Seat
    ).filter(
        models.Seat.show_id == booking.show_id,
        models.Seat.seat_number.in_(
            booking.seat_numbers
        )
    ).all()


    # Check all requested seats exist

    if len(seats) != len(
        booking.seat_numbers
    ):

        raise HTTPException(
            status_code=400,
            detail="One or more seats are invalid"
        )


    # ---------------------------------------------
    # CHECK AVAILABILITY
    # ---------------------------------------------

    unavailable_seats = [

        seat.seat_number

        for seat in seats

        if seat.status != "available"

    ]


    if unavailable_seats:

        raise HTTPException(
            status_code=400,
            detail={
                "message": "Some seats are already booked",
                "seats": unavailable_seats
            }
        )


    # ---------------------------------------------
    # CALCULATE TOTAL
    # ---------------------------------------------

    total_amount = (
        len(booking.seat_numbers)
        * show.price
    )


    # ---------------------------------------------
    # UPDATE SEATS
    # ---------------------------------------------

    for seat in seats:

        seat.status = "booked"


    # ---------------------------------------------
    # CREATE BOOKING
    # ---------------------------------------------

    new_booking = models.Booking(

        customer_name=
            booking.customer_name,

        customer_email=
            booking.customer_email,

        show_id=
            booking.show_id,

        seat_numbers=
            ",".join(
                booking.seat_numbers
            ),

        total_amount=
            total_amount

    )


    db.add(new_booking)

    db.commit()

    db.refresh(new_booking)


    # ---------------------------------------------
    # RESPONSE
    # ---------------------------------------------

    return {

        "message":
            "Booking confirmed successfully",

        "booking_id":
            new_booking.id,

        "customer":
            new_booking.customer_name,

        "show_id":
            new_booking.show_id,

        "seats":
            booking.seat_numbers,

        "total_amount":
            total_amount

    }
    # =========================================================
# GET BOOKINGS BY EMAIL
# =========================================================

@app.get("/bookings")
def get_bookings(
    email: str,
    db: Session = Depends(get_db)
):

    bookings = db.query(
        models.Booking
    ).filter(
        models.Booking.customer_email == email
    ).all()

    result = []

    for booking in bookings:

        show = db.query(
            models.Show
        ).filter(
            models.Show.id == booking.show_id
        ).first()

        movie = None
        theatre = None

        if show:

            movie = db.query(
                models.Movie
            ).filter(
                models.Movie.id == show.movie_id
            ).first()

            theatre = db.query(
                models.Theatre
            ).filter(
                models.Theatre.id == show.theatre_id
            ).first()

        result.append({

            "booking_id":
                booking.id,

            "customer_name":
                booking.customer_name,

            "customer_email":
                booking.customer_email,

            "movie":
                movie.title if movie else "Unknown",

            "theatre":
                theatre.name if theatre else "Unknown",

            "location":
                theatre.location if theatre else "Unknown",

            "show_date":
                str(show.show_date)
                if show else "",

            "show_time":
                str(show.show_time)
                if show else "",

            "seats":
                booking.seat_numbers,

            "total_amount":
                booking.total_amount

        })

    return result
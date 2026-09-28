from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    Date,
    Time,
    ForeignKey
)

from sqlalchemy.orm import relationship

from backend.database import Base


# =========================================================
# MOVIE
# =========================================================

class Movie(Base):

    __tablename__ = "movies"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    title = Column(
        String,
        nullable=False
    )

    genre = Column(
        String
    )

    rating = Column(
        Float
    )


# =========================================================
# THEATRE
# =========================================================

class Theatre(Base):

    __tablename__ = "theatres"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    name = Column(
        String,
        nullable=False
    )

    location = Column(
        String
    )


# =========================================================
# SHOW
# =========================================================

class Show(Base):

    __tablename__ = "shows"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    movie_id = Column(
        Integer,
        ForeignKey("movies.id")
    )

    theatre_id = Column(
        Integer,
        ForeignKey("theatres.id")
    )

    show_date = Column(
        Date
    )

    show_time = Column(
        Time
    )

    price = Column(
        Float
    )


# =========================================================
# SEAT
# =========================================================

class Seat(Base):

    __tablename__ = "seats"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    show_id = Column(
        Integer,
        ForeignKey("shows.id")
    )

    seat_number = Column(
        String
    )

    status = Column(
        String,
        default="available"
    )


# =========================================================
# BOOKING
# =========================================================

class Booking(Base):

    __tablename__ = "bookings"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    customer_name = Column(
        String
    )

    customer_email = Column(
        String
    )

    show_id = Column(
        Integer,
        ForeignKey("shows.id")
    )

    seat_numbers = Column(
        String
    )

    total_amount = Column(
        Float
    )
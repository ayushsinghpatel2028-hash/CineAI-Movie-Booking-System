import pandas as pd
import numpy as np

from xgboost import XGBRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error


# =========================================================
# CREATE TRAINING DATA
# =========================================================

np.random.seed(42)

data = pd.DataFrame({
    "day_of_week": np.random.randint(0, 7, 1000),
    "show_hour": np.random.randint(10, 23, 1000),
    "is_weekend": np.random.randint(0, 2, 1000),
    "movie_rating": np.round(
        np.random.uniform(5, 9.5, 1000), 1
    ),
    "ticket_price": np.random.randint(150, 500, 1000),
    "previous_bookings": np.random.randint(0, 100, 1000),
})


# =========================================================
# CREATE DEMAND TARGET
# =========================================================

data["demand"] = (
    data["previous_bookings"] * 0.45
    + data["movie_rating"] * 5
    + data["is_weekend"] * 20
    + np.where(
        data["show_hour"].between(18, 22),
        25,
        5
    )
    - data["ticket_price"] * 0.03
    + np.random.normal(0, 5, 1000)
)


# =========================================================
# FEATURES & TARGET
# =========================================================

X = data[
    [
        "day_of_week",
        "show_hour",
        "is_weekend",
        "movie_rating",
        "ticket_price",
        "previous_bookings",
    ]
]

y = data["demand"]


# =========================================================
# TRAIN TEST SPLIT
# =========================================================

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42
)


# =========================================================
# XGBOOST MODEL
# =========================================================

model = XGBRegressor(
    n_estimators=200,
    max_depth=5,
    learning_rate=0.05,
    random_state=42,
    objective="reg:squarederror"
)

model.fit(X_train, y_train)


# =========================================================
# MODEL EVALUATION
# =========================================================

predictions = model.predict(X_test)

mae = mean_absolute_error(
    y_test,
    predictions
)

print("=" * 50)
print("CineAI - XGBoost Demand Prediction")
print("=" * 50)

print(f"Mean Absolute Error: {mae:.2f}")


# =========================================================
# DEMAND PREDICTION FUNCTION
# =========================================================

def predict_demand(
    day_of_week,
    show_hour,
    is_weekend,
    movie_rating,
    ticket_price,
    previous_bookings
):

    input_data = pd.DataFrame([
        {
            "day_of_week": day_of_week,
            "show_hour": show_hour,
            "is_weekend": is_weekend,
            "movie_rating": movie_rating,
            "ticket_price": ticket_price,
            "previous_bookings": previous_bookings
        }
    ])

    prediction = model.predict(input_data)[0]

    prediction = max(0, prediction)

    return round(float(prediction), 2)


# =========================================================
# TEST PREDICTION
# =========================================================

if __name__ == "__main__":

    demand = predict_demand(
        day_of_week=5,
        show_hour=20,
        is_weekend=1,
        movie_rating=8.5,
        ticket_price=250,
        previous_bookings=60
    )

    print(f"Predicted Demand: {demand:.2f}")

    if demand >= 70:
        print("Demand Level: HIGH 🔥")

    elif demand >= 40:
        print("Demand Level: MEDIUM 🟡")

    else:
        print("Demand Level: LOW 🟢")
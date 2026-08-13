import sys
import os

# Add StayNear project root to Python path
sys.path.append(
    os.path.dirname(
        os.path.dirname(
            os.path.abspath(__file__)
        )
    )
)

import pickle

import pandas as pd

from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.cluster import KMeans
from sklearn.pipeline import Pipeline

from app import app
from database.db import db


# =========================================================
# TRAINING CONFIGURATION
# =========================================================

MODEL_PATH = os.path.join(
    os.path.dirname(__file__),
    "recommendation_model.pkl"
)


# =========================================================
# LOAD PROPERTY DATA
# =========================================================

def load_property_data():

    query = """
        SELECT
            p.property_id,
            p.property_name,
            p.property_type,
            p.city,
            p.area,
            p.monthly_rent,
            p.available_rooms,
            p.gender_preference,

            GROUP_CONCAT(
                a.amenity_name
                ORDER BY a.amenity_id
                SEPARATOR ', '
            ) AS amenities

        FROM properties p

        LEFT JOIN property_amenities pa
            ON p.property_id = pa.property_id

        LEFT JOIN amenities a
            ON pa.amenity_id = a.amenity_id

        WHERE p.available = 1
          AND p.property_status = 'Approved'

        GROUP BY
            p.property_id,
            p.property_name,
            p.property_type,
            p.city,
            p.area,
            p.monthly_rent,
            p.available_rooms,
            p.gender_preference

        ORDER BY p.property_id
    """

    result = db.session.execute(db.text(query))

    rows = result.fetchall()

    columns = result.keys()

    df = pd.DataFrame(
        rows,
        columns=columns
    )

    return df


# =========================================================
# PREPARE DATA
# =========================================================

def prepare_data(df):

    print("\n========================================")
    print("PROPERTY DATA")
    print("========================================")

    print(df.to_string(index=False))

    print("\nTotal properties:", len(df))

    # Missing amenities
    df["amenities"] = df["amenities"].fillna("")

    # Convert rent to numeric
    df["monthly_rent"] = pd.to_numeric(
        df["monthly_rent"],
        errors="coerce"
    )

    # Convert rooms to numeric
    df["available_rooms"] = pd.to_numeric(
        df["available_rooms"],
        errors="coerce"
    )

    # Fill missing numeric values
    df["monthly_rent"] = df["monthly_rent"].fillna(
        df["monthly_rent"].median()
    )

    df["available_rooms"] = df["available_rooms"].fillna(0)

    return df


# =========================================================
# CREATE FEATURES
# =========================================================

def create_features(df):

    # Convert amenities into individual binary columns
    all_amenities = set()

    for amenities in df["amenities"]:

        if amenities:

            items = [
                item.strip()
                for item in amenities.split(",")
                if item.strip()
            ]

            all_amenities.update(items)

    all_amenities = sorted(all_amenities)

    print("\n========================================")
    print("AMENITIES FOUND")
    print("========================================")

    print(all_amenities)

    # Create one column for each amenity
    for amenity in all_amenities:

        df[f"amenity_{amenity}"] = (
            df["amenities"]
            .apply(
                lambda x:
                1 if amenity in x.split(", ")
                else 0
            )
        )

    amenity_columns = [
        f"amenity_{amenity}"
        for amenity in all_amenities
    ]

    # Features used for clustering
    categorical_features = [
        "property_type",
        "city",
        "gender_preference"
    ]

    numeric_features = [
        "monthly_rent",
        "available_rooms"
    ]

    features = (
        categorical_features
        + numeric_features
        + amenity_columns
    )

    X = df[features].copy()

    return X, features


# =========================================================
# TRAIN MODEL
# =========================================================

def train_model():

    print("\n========================================")
    print("STAYNEAR RECOMMENDATION MODEL")
    print("========================================")

    with app.app_context():

        # -------------------------------------------------
        # LOAD DATA
        # -------------------------------------------------

        df = load_property_data()

        if df.empty:

            print("\nNo property data found.")

            return

        # -------------------------------------------------
        # PREPARE DATA
        # -------------------------------------------------

        df = prepare_data(df)

        # -------------------------------------------------
        # CREATE FEATURES
        # -------------------------------------------------

        X, feature_names = create_features(df)

        categorical_features = [
            "property_type",
            "city",
            "gender_preference"
        ]

        numeric_features = [
            "monthly_rent",
            "available_rooms"
        ]

        amenity_features = [
            column
            for column in feature_names
            if column.startswith("amenity_")
        ]

        # -------------------------------------------------
        # PREPROCESSING
        # -------------------------------------------------

        preprocessor = ColumnTransformer(

            transformers=[

                (
                    "categorical",

                    OneHotEncoder(
                        handle_unknown="ignore"
                    ),

                    categorical_features
                ),

                (
                    "numeric",

                    StandardScaler(),

                    numeric_features
                    + amenity_features
                )
            ]
        )

        # -------------------------------------------------
        # NUMBER OF CLUSTERS
        # -------------------------------------------------

        number_of_properties = len(df)

        number_of_clusters = min(
            4,
            number_of_properties
        )

        # -------------------------------------------------
        # K-MEANS MODEL
        # -------------------------------------------------

        kmeans = KMeans(
            n_clusters=number_of_clusters,
            random_state=42,
            n_init=10
        )

        model = Pipeline(

            steps=[

                (
                    "preprocessor",
                    preprocessor
                ),

                (
                    "clustering",
                    kmeans
                )
            ]
        )

        # -------------------------------------------------
        # TRAIN
        # -------------------------------------------------

        model.fit(X)

        # -------------------------------------------------
        # ASSIGN CLUSTERS
        # -------------------------------------------------

        df["cluster"] = model.predict(X)

        # -------------------------------------------------
        # SAVE MODEL
        # -------------------------------------------------

        model_data = {

            "model": model,

            "features": feature_names,

            "properties": df[
                [
                    "property_id",
                    "property_name",
                    "cluster"
                ]
            ].to_dict(
                orient="records"
            )
        }

        with open(
            MODEL_PATH,
            "wb"
        ) as file:

            pickle.dump(
                model_data,
                file
            )

        # -------------------------------------------------
        # DISPLAY RESULTS
        # -------------------------------------------------

        print("\n========================================")
        print("TRAINING COMPLETED")
        print("========================================")

        print(
            "Properties used:",
            len(df)
        )

        print(
            "Clusters created:",
            number_of_clusters
        )

        print(
            "Model saved at:",
            MODEL_PATH
        )

        print("\n========================================")
        print("PROPERTY CLUSTERS")
        print("========================================")

        print(
            df[
                [
                    "property_id",
                    "property_name",
                    "cluster"
                ]
            ].to_string(index=False)
        )


# =========================================================
# RUN
# =========================================================

if __name__ == "__main__":

    train_model()
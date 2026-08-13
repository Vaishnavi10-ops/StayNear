import os
import pickle
import pandas as pd

from database.db import db
from models.property import Property
from sqlalchemy import text


# ============================================================
# LOAD TRAINED MODEL
# ============================================================

MODEL_PATH = os.path.join(
    os.path.dirname(__file__),
    "recommendation_model.pkl"
)

with open(MODEL_PATH, "rb") as file:
    model_data = pickle.load(file)


# Saved model information
model = model_data["model"]

FEATURES = model_data["features"]

TRAINED_PROPERTIES = model_data.get(
    "properties",
    []
)


# ============================================================
# GET CURRENT PROPERTY DATA FROM DATABASE
# ============================================================

def get_property_data():

    properties = Property.query.filter_by(
        available=True,
        property_status="Approved"
    ).all()

    data = []

    for property in properties:

        # ----------------------------------------------------
        # Get amenities for this property
        # ----------------------------------------------------

        rows = db.session.execute(
            text("""
                SELECT a.amenity_name
                FROM property_amenities pa

                JOIN amenities a
                    ON pa.amenity_id = a.amenity_id

                WHERE pa.property_id = :property_id
            """),
            {
                "property_id": property.property_id
            }
        ).fetchall()

        amenity_names = [
            row[0]
            for row in rows
        ]

        # ----------------------------------------------------
        # Create property record
        # ----------------------------------------------------

        data.append({

            "property_id":
                property.property_id,

            "property_name":
                property.property_name,

            "property_type":
                property.property_type,

            "city":
                property.city,

            "area":
                property.area,

            "monthly_rent":
                float(property.monthly_rent or 0),

            "available_rooms":
                int(property.available_rooms or 0),

            "gender_preference":
                property.gender_preference,

            "amenities":
                amenity_names
        })

    return pd.DataFrame(data)


# ============================================================
# PREPARE PROPERTY FEATURES
# ============================================================

def prepare_property_features(properties_df):

    rows = []

    for _, property in properties_df.iterrows():

        row = {}

        # ----------------------------------------------------
        # Basic features
        # ----------------------------------------------------

        row["property_type"] = (
            property["property_type"]
            or "PG"
        )

        row["city"] = (
            property["city"]
            or "Nashik"
        )

        row["gender_preference"] = (
            property["gender_preference"]
            or "Co-ed"
        )

        row["monthly_rent"] = float(
            property["monthly_rent"] or 0
        )

        row["available_rooms"] = int(
            property["available_rooms"] or 0
        )

        # ----------------------------------------------------
        # Property amenities
        # ----------------------------------------------------

        property_amenities = [
            str(amenity).strip().lower()
            for amenity in property["amenities"]
        ]

        # ----------------------------------------------------
        # Create amenity columns
        # ----------------------------------------------------

        for feature in FEATURES:

            if feature.startswith("amenity_"):

                amenity_name = feature.replace(
                    "amenity_",
                    "",
                    1
                )

                row[feature] = int(
                    amenity_name.strip().lower()
                    in property_amenities
                )

        rows.append(row)

    return pd.DataFrame(
        rows,
        columns=FEATURES
    )


# ============================================================
# CREATE USER PREFERENCE
# ============================================================

def create_user_preference(
    budget,
    property_type=None,
    city=None,
    gender_preference=None,
    amenities=None
):

    # --------------------------------------------------------
    # Normalize amenities
    # --------------------------------------------------------

    if amenities is None:
        amenities = []

    if isinstance(amenities, str):

        amenities = [
            item.strip()
            for item in amenities.split(",")
            if item.strip()
        ]

    # --------------------------------------------------------
    # Create user data
    # --------------------------------------------------------

    user_data = {}

    # --------------------------------------------------------
    # Categorical features
    # --------------------------------------------------------

    user_data["property_type"] = (
        property_type
        if property_type
        else "PG"
    )

    user_data["city"] = (
        city
        if city
        else "Nashik"
    )

    user_data["gender_preference"] = (
        gender_preference
        if gender_preference
        else "Co-ed"
    )

    # --------------------------------------------------------
    # Numeric features
    # --------------------------------------------------------

    user_data["monthly_rent"] = float(
        budget
    )

    # User wants an available property
    user_data["available_rooms"] = 1

    # --------------------------------------------------------
    # User amenities
    # --------------------------------------------------------

    user_amenities = [
        str(amenity).strip().lower()
        for amenity in amenities
    ]

    # --------------------------------------------------------
    # Create amenity feature columns
    # --------------------------------------------------------

    for feature in FEATURES:

        if feature.startswith("amenity_"):

            amenity_name = feature.replace(
                "amenity_",
                "",
                1
            )

            user_data[feature] = int(
                amenity_name.strip().lower()
                in user_amenities
            )

    return pd.DataFrame(
        [user_data],
        columns=FEATURES
    )


# ============================================================
# RECOMMEND PROPERTIES
# ============================================================

def recommend_properties(
    budget,
    property_type=None,
    city=None,
    gender_preference=None,
    amenities=None,
    top_n=5
):

    print("\n========================================")
    print("STAYNEAR RECOMMENDATION ENGINE")
    print("========================================")

    # ========================================================
    # GET CURRENT DATABASE PROPERTIES
    # ========================================================

    properties_df = get_property_data()

    if properties_df.empty:

        print("No available approved properties found.")

        return []

    print(
        "Properties available for recommendation:",
        len(properties_df)
    )

    # ========================================================
    # NORMALIZE BUDGET
    # ========================================================

    try:
        budget = float(budget)

    except (ValueError, TypeError):
        budget = 10000

    # ========================================================
    # NORMALIZE USER INPUT
    # ========================================================

    if property_type:
        property_type = str(property_type).strip()

    if city:
        city = str(city).strip()

    if gender_preference:
        gender_preference = str(
            gender_preference
        ).strip()

    # ========================================================
    # CREATE PROPERTY FEATURES
    # ========================================================

    X_properties = prepare_property_features(
        properties_df
    )

    # ========================================================
    # CREATE USER FEATURES
    # ========================================================

    X_user = create_user_preference(
        budget=budget,
        property_type=property_type,
        city=city,
        gender_preference=gender_preference,
        amenities=amenities
    )

    # ========================================================
    # PREDICT USER CLUSTER
    # ========================================================

    try:

        user_cluster = model.predict(
            X_user
        )[0]

    except Exception as e:

        print(
            "USER CLUSTER ERROR:",
            e
        )

        return []

    print(
        "User cluster:",
        user_cluster
    )

    # ========================================================
    # PREDICT PROPERTY CLUSTERS
    # ========================================================

    try:

        property_clusters = model.predict(
            X_properties
        )

    except Exception as e:

        print(
            "PROPERTY CLUSTER ERROR:",
            e
        )

        return []

    properties_df["cluster"] = property_clusters

    # ========================================================
    # CLUSTER MATCH
    # ========================================================

    properties_df["cluster_match"] = (
        properties_df["cluster"] == user_cluster
    )

    # ========================================================
    # BUDGET MATCH
    # ========================================================

    max_budget = budget * 1.20

    properties_df["budget_match"] = (
        properties_df["monthly_rent"] <= max_budget
    )

    # ========================================================
    # PROPERTY TYPE MATCH
    # ========================================================

    if property_type:

        properties_df["type_match"] = (

            properties_df["property_type"]
            .fillna("")
            .astype(str)
            .str.lower()
            ==
            property_type.lower()

        )

    else:

        properties_df["type_match"] = True

    # ========================================================
    # GENDER MATCH
    # ========================================================

    if gender_preference:

        property_gender = (

            properties_df[
                "gender_preference"
            ]
            .fillna("")
            .astype(str)
            .str.lower()

        )

        requested_gender = gender_preference.lower()

        properties_df["gender_match"] = (

            property_gender == requested_gender

        ) | (

            property_gender == "co-ed"

        )

    else:

        properties_df["gender_match"] = True

    # ========================================================
    # CITY MATCH
    # ========================================================

    if city:

        properties_df["city_match"] = (

            properties_df["city"]
            .fillna("")
            .astype(str)
            .str.lower()
            ==
            city.lower()

        )

    else:

        properties_df["city_match"] = True

    # ========================================================
    # BUDGET SCORE
    # ========================================================

    properties_df["budget_score"] = (

        1
        -
        (
            abs(
                properties_df["monthly_rent"]
                -
                budget
            )
            /
            max(budget, 1)
        )

    ).clip(
        lower=0,
        upper=1
    )

    # ========================================================
    # AMENITY SCORE
    # ========================================================

    if amenities is None:
        amenities = []

    if isinstance(amenities, str):

        amenities = [
            item.strip()
            for item in amenities.split(",")
            if item.strip()
        ]

    user_amenities = [
        str(amenity).strip().lower()
        for amenity in amenities
    ]

    def calculate_amenity_score(property_amenities):

        if not user_amenities:
            return 0

        property_amenities_lower = [

            str(amenity)
            .strip()
            .lower()

            for amenity in property_amenities

        ]

        matched = sum(

            1

            for amenity in user_amenities

            if amenity in property_amenities_lower

        )

        return matched / len(user_amenities)

    properties_df["amenity_score"] = (

        properties_df["amenities"]
        .apply(calculate_amenity_score)

    )

    # ========================================================
    # FINAL RECOMMENDATION SCORE
    # ========================================================

    properties_df["score"] = 0.0

    # --------------------------------------------------------
    # 1. PROPERTY TYPE
    # --------------------------------------------------------

    if property_type:

        properties_df["score"] += (

            properties_df["type_match"]
            .astype(int)
            * 0.30

        )

    else:

        properties_df["score"] += 0.20

    # --------------------------------------------------------
    # 2. GENDER
    # --------------------------------------------------------

    if gender_preference:

        properties_df["score"] += (

            properties_df["gender_match"]
            .astype(int)
            * 0.20

        )

    else:

        properties_df["score"] += 0.15

    # --------------------------------------------------------
    # 3. CITY
    # --------------------------------------------------------

    if city:

        properties_df["score"] += (

            properties_df["city_match"]
            .astype(int)
            * 0.15

        )

    else:

        properties_df["score"] += 0.10

    # --------------------------------------------------------
    # 4. BUDGET
    # --------------------------------------------------------

    properties_df["score"] += (

        properties_df["budget_match"]
        .astype(int)
        * 0.15

    )

    # --------------------------------------------------------
    # 5. ML CLUSTER MATCH
    # --------------------------------------------------------

    properties_df["score"] += (

        properties_df["cluster_match"]
        .astype(int)
        * 0.10

    )

    # --------------------------------------------------------
    # 6. BUDGET CLOSENESS
    # --------------------------------------------------------

    properties_df["score"] += (

        properties_df["budget_score"]
        * 0.05

    )

    # --------------------------------------------------------
    # 7. AMENITY MATCH
    # --------------------------------------------------------

    properties_df["score"] += (

        properties_df["amenity_score"]
        * 0.05

    )

    # ========================================================
    # HARD FILTERING / PRIORITY
    # ========================================================

    if property_type:

        matching_type = properties_df[
            properties_df["type_match"]
        ]

        non_matching_type = properties_df[
            ~properties_df["type_match"]
        ]

    else:

        matching_type = properties_df
        non_matching_type = properties_df.iloc[0:0]

    # ========================================================
    # GENDER PRIORITY
    # ========================================================

    if gender_preference:

        matching_gender = matching_type[
            matching_type["gender_match"]
        ]

        other_gender = matching_type[
            ~matching_type["gender_match"]
        ]

    else:

        matching_gender = matching_type
        other_gender = matching_type.iloc[0:0]

    # ========================================================
    # SORT
    # ========================================================

    matching_gender = matching_gender.sort_values(
        by=[
            "score",
            "budget_score"
        ],
        ascending=False
    )

    other_gender = other_gender.sort_values(
        by=[
            "score",
            "budget_score"
        ],
        ascending=False
    )

    non_matching_type = non_matching_type.sort_values(
        by=[
            "score",
            "budget_score"
        ],
        ascending=False
    )

    # ========================================================
    # FINAL RECOMMENDATION ORDER
    # ========================================================

    recommendations = pd.concat(
        [
            matching_gender,
            other_gender,
            non_matching_type
        ],
        ignore_index=True
    )

    # ========================================================
    # MATCH PERCENTAGE
    # ========================================================

    recommendations["match_percentage"] = (

        recommendations["score"]
        * 100

    ).clip(
        lower=0,
        upper=100
    ).round(0).astype(int)

    # ========================================================
    # DEBUG OUTPUT
    # ========================================================

    print("\n========================================")
    print("RECOMMENDATIONS")
    print("========================================")

    print(

        recommendations[
            [
                "property_id",
                "property_name",
                "property_type",
                "city",
                "gender_preference",
                "monthly_rent",
                "cluster",
                "score",
                "match_percentage"
            ]
        ]
        .head(top_n)
        .to_string(index=False)

    )

    # ========================================================
    # RETURN TOP N
    # ========================================================

    return (

        recommendations
        .head(top_n)
        .to_dict(
            orient="records"
        )

    )
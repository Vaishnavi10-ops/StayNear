from flask import Blueprint, render_template, request, session, redirect, url_for
from database.db import db
from ml.recommend import recommend_properties
from models.amenity import Amenity
from models.property import Property
from sqlalchemy import or_, text
from models.booking import Booking
from models.user import User
from datetime import datetime
from models.review import Review
from flask import flash


user = Blueprint("user", __name__)

@user.route("/user/home")
def home():

    if "user_id" not in session or session["role"] != "User":
        return redirect(url_for("auth.login"))

    return render_template("user/home.html")


@user.route("/user/search")
def search_properties():

    if "user_id" not in session or session["role"] != "User":
        return redirect(url_for("auth.login"))

    # ==========================================
    # GET USER PREFERENCES
    # ==========================================

    location = request.args.get("location", "").strip()
    property_type = request.args.get("property_type", "").strip()
    budget = request.args.get("budget", "").strip()
    gender = request.args.get("gender", "").strip()
    amenities = request.args.getlist("amenities")

    print("========================================")
    print("STAYNEAR RECOMMENDATION SEARCH")
    print("Location:", location)
    print("Property Type:", property_type)
    print("Budget:", budget)
    print("Gender:", gender)
    print("Amenities:", amenities)
    print("========================================")

    # ==========================================
    # VALIDATE BUDGET
    # ==========================================

    try:
        budget_value = float(budget) if budget else 10000

    except (ValueError, TypeError):
        budget_value = 10000

    # ==========================================
    # INITIALIZE RECOMMENDATION VARIABLES
    # ==========================================

    recommended_ids = []

    # IMPORTANT:
    # Always initialize this before try block.
    # This prevents UnboundLocalError.
    recommendation_scores = {}

    # ==========================================
    # GET ML RECOMMENDATIONS
    # ==========================================

    try:

        recommended_data = recommend_properties(

            budget=budget_value,

            property_type=property_type or None,

            city=location or None,

            gender_preference=gender or None,

            amenities=amenities,

            top_n=10

        )

        # ------------------------------------------
        # Store IDs
        # ------------------------------------------

        candidate_ids = [
            item["property_id"]
            for item in recommended_data
        ]

        # ------------------------------------------
        # Store MATCH PERCENTAGE
        # ------------------------------------------

        recommendation_scores = {

            item["property_id"]: float(
                item.get("match_percentage", 0)
            )

            for item in recommended_data

        }

        print("\nML recommended candidates:")
        print(candidate_ids)

        # ==========================================
        # GET ACTUAL PROPERTY OBJECTS
        # ==========================================

        if candidate_ids:

            candidate_properties = Property.query.filter(

                Property.property_id.in_(candidate_ids),

                Property.property_status == "Approved",

                Property.available == True

            ).all()

        else:

            candidate_properties = []

        # ==========================================
        # VALIDATE ML RECOMMENDATIONS
        # ==========================================

        valid_recommendations = []

        for property in candidate_properties:

            # --------------------------------------
            # Property Type
            # --------------------------------------

            if property_type:

                if (
                    not property.property_type
                    or
                    property.property_type.lower()
                    != property_type.lower()
                ):

                    continue

            # --------------------------------------
            # Gender
            # --------------------------------------

            if gender:

                property_gender = (
                    property.gender_preference or ""
                ).lower()

                requested_gender = gender.lower()

                if (

                    property_gender != requested_gender

                    and

                    property_gender != "co-ed"

                ):

                    continue

            # --------------------------------------
            # Location
            # --------------------------------------

            if location:

                location_lower = location.lower()

                city_match = (

                    location_lower
                    in (property.city or "").lower()

                )

                area_match = (

                    location_lower
                    in (property.area or "").lower()

                )

                address_match = (

                    location_lower
                    in (property.address or "").lower()

                )

                if not (
                    city_match
                    or area_match
                    or address_match
                ):

                    continue

            # --------------------------------------
            # Budget
            # --------------------------------------

            if budget:

                if float(
                    property.monthly_rent or 0
                ) > budget_value:

                    continue

            # --------------------------------------
            # Valid Recommendation
            # --------------------------------------

            valid_recommendations.append(property)

        # ==========================================
        # KEEP ML RECOMMENDATION ORDER
        # ==========================================

        property_map = {

            property.property_id: property

            for property in valid_recommendations

        }

        recommended_ids = [

            property_id

            for property_id in candidate_ids

            if property_id in property_map

        ]

        # ------------------------------------------
        # Maximum 5 AI Recommendations
        # ------------------------------------------

        recommended_ids = recommended_ids[:5]

        print("\nValidated AI recommendations:")
        print(recommended_ids)

    except Exception as e:

        print("========================================")
        print("RECOMMENDATION ERROR")
        print(e)
        print("========================================")

        recommended_ids = []

        # Keep dictionary safe if recommendation fails
        recommendation_scores = {}

    # ==========================================
    # GET RECOMMENDED PROPERTY OBJECTS
    # ==========================================

    recommended_properties = []

    if recommended_ids:

        property_objects = Property.query.filter(

            Property.property_id.in_(recommended_ids),

            Property.property_status == "Approved",

            Property.available == True

        ).all()

        property_map = {

            property.property_id: property

            for property in property_objects

        }

        recommended_properties = [

            property_map[property_id]

            for property_id in recommended_ids

            if property_id in property_map

        ]

        # ==========================================
        # ATTACH MATCH PERCENTAGE
        # ==========================================

        for property in recommended_properties:

            property.match_percentage = round(

                recommendation_scores.get(
                    property.property_id,
                    0
                )

            )

    # ==========================================
    # GET NORMAL MATCHING PROPERTIES
    # ==========================================

    query = Property.query.filter(

        Property.property_status == "Approved",

        Property.available == True

    )

    # ------------------------------------------
    # Location
    # ------------------------------------------

    if location:

        query = query.filter(

            or_(

                Property.city.ilike(
                    f"%{location}%"
                ),

                Property.area.ilike(
                    f"%{location}%"
                ),

                Property.address.ilike(
                    f"%{location}%"
                )

            )

        )

    # ------------------------------------------
    # Property Type
    # ------------------------------------------

    if property_type:

        query = query.filter(

            Property.property_type
            == property_type

        )

    # ------------------------------------------
    # Gender
    # ------------------------------------------

    if gender:

        query = query.filter(

            or_(

                Property.gender_preference
                == gender,

                Property.gender_preference
                == "Co-ed"

            )

        )

    # ------------------------------------------
    # Budget
    # ------------------------------------------

    if budget:

        query = query.filter(

            Property.monthly_rent
            <= budget_value

        )

    # ==========================================
    # REMOVE AI RECOMMENDATIONS
    # FROM NORMAL PROPERTY LIST
    # ==========================================

    if recommended_ids:

        query = query.filter(

            ~Property.property_id.in_(
                recommended_ids
            )

        )

    # ==========================================
    # GET NORMAL PROPERTIES
    # ==========================================

    normal_properties = query.order_by(

        Property.created_at.desc()

    ).all()

    # ==========================================
    # COMBINE RESULTS
    # ==========================================

    properties = (

        recommended_properties
        +
        normal_properties

    )

    # ==========================================
    # DEBUG
    # ==========================================

    print("\n========================================")
    print("FINAL PROPERTY RESULTS")
    print("========================================")

    print(
        "AI Recommendations:",
        recommended_ids
    )

    print(
        "Recommendation Scores:",
        recommendation_scores
    )

    print(
        "Total properties shown:",
        len(properties)
    )

    # ==========================================
    # SEND TO TEMPLATE
    # ==========================================

    return render_template(

        "user/properties.html",

        properties=properties,

        recommended_ids=recommended_ids,

        recommendation_scores=recommendation_scores,

        location=location,

        property_type=property_type,

        budget=budget,

        gender=gender,

        recommended=True

    )


@user.route("/properties")
def properties():

    location = request.args.get("location", "").strip()
    property_type = request.args.get("property_type", "").strip()
    max_budget = request.args.get("max_budget", "").strip()
    gender = request.args.get("gender", "").strip()
    print("SELECTED GENDER:", repr(gender))

    query = Property.query.filter(
        Property.property_status == "Approved"
    )

    if location:
        query = query.filter(
            db.or_(
                Property.city.ilike(f"%{location}%"),
                Property.area.ilike(f"%{location}%")
            )
        )

    if property_type:
        query = query.filter(
            Property.property_type == property_type
        )

    if gender:
        query = query.filter(
            Property.gender_preference == gender
        )

    if max_budget:
        try:
            max_budget_value = float(max_budget)

            query = query.filter(
                Property.monthly_rent <= max_budget_value
            )

        except ValueError:
            pass
    
    properties = query.order_by(
        Property.created_at.desc()
    ).all()


    return render_template(
    "user/properties.html",
    properties=properties,
    location=location,
    property_type=property_type,
    max_budget=max_budget,
    gender=gender
)

@user.route("/property/<int:property_id>")
def view_property(property_id):

    # -----------------------------------------
    # GET PROPERTY
    # -----------------------------------------

    property = Property.query.filter_by(
        property_id=property_id,
        available=True,
        property_status="Approved"
    ).first_or_404()

    # -----------------------------------------
    # GET PROPERTY AMENITY IDs
    # -----------------------------------------

    amenity_ids = db.session.execute(
        text("""
            SELECT amenity_id
            FROM property_amenities
            WHERE property_id = :property_id
        """),
        {
            "property_id": property.property_id
        }
    ).scalars().all()

    # -----------------------------------------
    # GET AMENITY DETAILS
    # -----------------------------------------

    amenities = []

    if amenity_ids:

        amenities = Amenity.query.filter(
            Amenity.amenity_id.in_(amenity_ids)
        ).all()

    # -----------------------------------------
    # ATTACH AMENITIES TO PROPERTY
    # -----------------------------------------

    property.amenities = amenities

    # -----------------------------------------
    # DEBUG
    # -----------------------------------------

    print("====================================")
    print("PROPERTY:", property.property_name)
    print("AMENITIES:", [a.amenity_name for a in amenities])
    print("====================================")

    # -----------------------------------------
    # DISPLAY PROPERTY
    # -----------------------------------------

    return render_template(
        "user/view_property.html",
        property=property
    )

@user.route("/user/book-visit/<int:property_id>", methods=["GET", "POST"])
def book_visit(property_id):

    if "user_id" not in session or session["role"] != "User":
        return redirect(url_for("auth.login"))

    property = Property.query.filter_by(
        property_id=property_id,
        available=True,
        property_status="Approved"
    ).first_or_404()

    if request.method == "POST":

        visit_date = request.form.get("visit_date")
        visit_time = request.form.get("visit_time")
        message = request.form.get("message", "").strip()

        if not visit_date or not visit_time:
            return render_template(
                "user/book_visit.html",
                property=property
            )

        try:
            visit_date_obj = datetime.strptime(
                visit_date,
                "%Y-%m-%d"
            ).date()

            visit_time_obj = datetime.strptime(
                visit_time,
                "%H:%M"
            ).time()

        except ValueError:
            return render_template(
                "user/book_visit.html",
                property=property
            )

        booking = Booking(
            property_id=property.property_id,
            user_id=session["user_id"],
            visit_date=visit_date_obj,
            visit_time=visit_time_obj,
            message=message,
            booking_status="Pending"
        )

        db.session.add(booking)
        db.session.commit()

        return redirect(
            url_for("user.my_bookings")
        )

    return render_template(
        "user/book_visit.html",
        property=property
    )


@user.route("/cancel-booking/<int:booking_id>", methods=["POST"])
def cancel_booking(booking_id):

    if "user_id" not in session or session["role"] != "User":
        return redirect(url_for("auth.login"))

    booking = Booking.query.filter_by(
        booking_id=booking_id,
        user_id=session["user_id"]
    ).first_or_404()

    # Only Pending bookings can be cancelled
    if booking.booking_status == "Pending":
        booking.booking_status = "Cancelled"
        db.session.commit()

    return redirect(url_for("user.my_bookings"))

@user.route("/user/my-bookings")
def my_bookings():

    if "user_id" not in session or session["role"] != "User":
        return redirect(url_for("auth.login"))

    bookings = Booking.query.filter_by(
        user_id=session["user_id"]
    ).order_by(
        Booking.created_at.desc()
    ).all()

    return render_template(
        "user/my_bookings.html",
        bookings=bookings
    )

@user.route("/rate-property/<int:property_id>", methods=["POST"])
def rate_property(property_id):

    if "user_id" not in session or session["role"] != "User":
        return redirect(url_for("auth.login"))

    rating = request.form.get("rating")

    # Validate rating
    try:
        rating = int(rating)
    except (ValueError, TypeError):
        return redirect(url_for("user.my_bookings"))

    if rating < 1 or rating > 5:
        return redirect(url_for("user.my_bookings"))

    # Check that the user has a completed booking
    booking = Booking.query.filter_by(
        user_id=session["user_id"],
        property_id=property_id,
        booking_status="Completed"
    ).first()

    if not booking:
        return redirect(url_for("user.my_bookings"))

    # Check whether the user already rated this property
    existing_rating = Review.query.filter_by(
        user_id=session["user_id"],
        property_id=property_id
    ).first()

    if existing_rating:

        # Update existing rating
        existing_rating.rating = rating

    else:

        # Create new rating
        new_rating = Review(
            user_id=session["user_id"],
            property_id=property_id,
            rating=rating
        )

        db.session.add(new_rating)

    db.session.commit()

    flash("Rating submitted successfully!", "success")

    return redirect(url_for("user.my_bookings"))


@user.route("/user/profile")
def profile():

    if "user_id" not in session or session["role"] != "User":
        return redirect(url_for("auth.login"))

    user = User.query.filter_by(
        user_id=session["user_id"]
    ).first_or_404()

    return render_template(
        "user/profile.html",
        user=user
    )
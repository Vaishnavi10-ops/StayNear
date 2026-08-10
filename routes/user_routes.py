from flask import Blueprint, render_template, request, session, redirect, url_for
from database.db import db
from models.property import Property
from sqlalchemy import or_
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

    location = request.args.get("location", "").strip()
    property_type = request.args.get("property_type", "").strip()
    budget = request.args.get("budget", "").strip()
    gender = request.args.get("gender", "").strip()

    query = Property.query

    # Location search
    if location:
        query = query.filter(
            or_(
                Property.city.ilike(f"%{location}%"),
                Property.area.ilike(f"%{location}%"),
                Property.address.ilike(f"%{location}%")
            )
        )

    # Property type
    if property_type:
        query = query.filter(
            Property.property_type == property_type
        )

    # Budget
    if budget:
        query = query.filter(
            Property.monthly_rent <= float(budget)
        )

    # Gender preference
    # Gender preference - STRICT
    if gender:
        query = query.filter(
            Property.gender_preference == gender
        )

    # Only approved properties should be visible to users
    query = query.filter(
        Property.property_status == "Approved"
    )

    properties = query.order_by(
        Property.created_at.desc()
    ).all()

    return render_template(
        "user/properties.html",
        properties=properties,
        location=location,
        property_type=property_type,
        budget=budget,
        gender=gender
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

    property = Property.query.filter_by(
        property_id=property_id,
        available=True,
        property_status="Approved"
    ).first_or_404()

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
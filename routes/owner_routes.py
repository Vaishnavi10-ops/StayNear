from datetime import datetime

from flask import Blueprint, current_app, render_template, request, redirect, url_for, flash, session
from models.property import Property
from database.db import db
from models.booking import Booking
from models.owner import Owner
from models.review import Review
import os
from werkzeug.utils import secure_filename
from models.property_image import PropertyImage
from sqlalchemy import extract, or_, func


owner = Blueprint("owner", __name__)

@owner.route("/owner/dashboard")
def dashboard():

    if "user_id" not in session or session["role"] != "Owner":
        return redirect(url_for("auth.login"))

    owner_id = session["user_id"]

    # --------------------------------
    # Total properties
    # --------------------------------

    properties = Property.query.filter_by(
        owner_id=owner_id
    ).all()

    total_properties = len(properties)

    # --------------------------------
    # Active properties
    # --------------------------------

    active_properties = Property.query.filter_by(
        owner_id=owner_id,
        property_status="Approved"
    ).count()

    # --------------------------------
    # Property IDs
    # --------------------------------

    property_ids = [
        property.property_id
        for property in properties
    ]

    # --------------------------------
    # Total bookings
    # --------------------------------

    total_bookings = 0

    if property_ids:

        total_bookings = Booking.query.filter(
            Booking.property_id.in_(property_ids)
        ).count()

    # --------------------------------
    # Booking trends
    # --------------------------------

    booking_trends = [0] * 12

    if property_ids:

        results = db.session.query(
            extract("month", Booking.created_at).label("month"),
            func.count(Booking.booking_id).label("count")
        ).filter(
            Booking.property_id.in_(property_ids)
        ).group_by(
            extract("month", Booking.created_at)
        ).all()

        for row in results:

            month = int(row.month)
            count = int(row.count)

            booking_trends[month - 1] = count

    # --------------------------------
    # Dashboard
    # --------------------------------

    return render_template(
        "owner/dashboard.html",
        total_properties=total_properties,
        active_properties=active_properties,
        total_bookings=total_bookings,
        booking_trends=booking_trends
    )

@owner.route("/owner/add-property", methods=["GET", "POST"])
def add_property():

    if "user_id" not in session or session["role"] != "Owner":
        return redirect(url_for("auth.login"))

    if request.method == "POST":

        property = Property(

    owner_id=session["user_id"],

    property_name=request.form["property_name"],
    property_type=request.form["property_type"],
    gender_preference=request.form["gender_preference"],

    address=request.form["address"],
    city=request.form["city"],
    area=request.form["area"],
    pincode=request.form["pincode"],

    monthly_rent=request.form["monthly_rent"],
    security_deposit=request.form["security_deposit"] or 0,
    available_rooms=request.form["available_rooms"],

    description=request.form["description"],
    images = request.files.getlist("property_images")
)

        try:
            db.session.add(property)
            db.session.commit()
            images = request.files.getlist("images")

            for image in images:

                if image.filename != "":

                    filename = secure_filename(image.filename)

                    save_path = os.path.join(current_app.config["UPLOAD_FOLDER"],filename)

                    image.save(save_path)

                    property_image = PropertyImage(

                        property_id=property.property_id,

                        image_path=f"uploads/properties/{filename}"

                    )

                    db.session.add(property_image)

            db.session.commit()
            
            flash("Property added successfully!", "success")
            return redirect(url_for("owner.add_property"))

        except Exception as e:
            db.session.rollback()
            flash(f"Error: {e}", "error")

    return render_template("owner/add_property.html")


@owner.route("/owner/my-properties")
def my_properties():

    if "user_id" not in session or session["role"] != "Owner":
        return redirect(url_for("auth.login"))

    # Get search and filter values
    search = request.args.get("search", "").strip()
    status = request.args.get("status", "").strip()

    # Start with logged-in owner's properties
    query = Property.query.filter_by(
        owner_id=session["user_id"]
    )

    # Search by property name, city, area or property type
    if search:
        query = query.filter(
            or_(
                Property.property_name.ilike(f"%{search}%"),
                Property.city.ilike(f"%{search}%"),
                Property.area.ilike(f"%{search}%"),
                Property.property_type.ilike(f"%{search}%")
            )
        )

    # Filter by status
    if status and status != "All":
        query = query.filter(
            Property.property_status == status
        )

    # Latest properties first
    properties = query.order_by(
        Property.created_at.desc()
    ).all()

    return render_template(
        "owner/my_properties.html",
        properties=properties,
        search=search,
        status=status
    )

@owner.route("/owner/bookings")
def bookings():

    if "user_id" not in session or session["role"] != "Owner":
        return redirect(url_for("auth.login"))

    # Search and filter values
    search = request.args.get("search", "").strip()
    status = request.args.get("status", "").strip()

    # Get properties belonging to this owner
    owner_properties = Property.query.filter_by(
        owner_id=session["user_id"]
    ).all()

    property_ids = [
        property.property_id
        for property in owner_properties
    ]

    # No properties = no bookings
    if not property_ids:

        bookings = []

    else:

        query = Booking.query.filter(
            Booking.property_id.in_(property_ids)
        )

        # Search by property name
        if search:

            query = query.join(
                Property,
                Booking.property_id == Property.property_id
            ).filter(
                Property.property_name.ilike(
                    f"%{search}%"
                )
            )

        # Filter by booking status
        if status and status != "All":

            query = query.filter(
                Booking.booking_status == status
            )

        # Latest bookings first
        bookings = query.order_by(
            Booking.created_at.desc()
        ).all()

    return render_template(
        "owner/bookings.html",
        bookings=bookings,
        search=search,
        status=status
    )

@owner.route("/owner/booking/<int:booking_id>/confirm", methods=["POST"])
def confirm_booking(booking_id):

    if "user_id" not in session or session["role"] != "Owner":
        return redirect(url_for("auth.login"))

    booking = Booking.query.join(
        Property
    ).filter(
        Booking.booking_id == booking_id,
        Property.owner_id == session["user_id"]
    ).first_or_404()

    booking.status = "Confirmed"

    db.session.commit()

    flash("Booking confirmed successfully!", "success")

    return redirect(url_for("owner.bookings"))


@owner.route("/owner/profile", methods=["GET", "POST"])
def profile():

    if "user_id" not in session or session["role"] != "Owner":
        return redirect(url_for("auth.login"))

    owner_user = Owner.query.filter_by(
        owner_id=session["user_id"]
    ).first_or_404()

    if request.method == "POST":

        owner_user.full_name = request.form["full_name"]
        owner_user.email = request.form["email"]
        owner_user.phone = request.form["phone"]

        new_password = request.form.get("password", "").strip()

        if new_password:
            owner_user.password = new_password

        db.session.commit()

        flash(
            "Profile updated successfully!",
            "success"
        )

        return redirect(
            url_for("owner.profile")
        )

    return render_template(
        "owner/profile.html",
        owner=owner_user
    )


@owner.route("/owner/property/<int:property_id>")
def view_property(property_id):

    if "user_id" not in session or session["role"] != "Owner":
        return redirect(url_for("auth.login"))

    property = Property.query.filter_by(
        property_id=property_id,
        owner_id=session["user_id"]
    ).first_or_404()

    return render_template(
        "owner/view_property.html",
        property=property
    )

@owner.route("/owner/property/<int:property_id>/edit", methods=["GET", "POST"])
def edit_property(property_id):

    # Check owner login
    if "user_id" not in session or session["role"] != "Owner":
        return redirect(url_for("auth.login"))

    # Find only this owner's property
    property = Property.query.filter_by(
        property_id=property_id,
        owner_id=session["user_id"]
    ).first_or_404()

    # When form is submitted
    if request.method == "POST":

        property.property_name = request.form["property_name"]
        property.property_type = request.form["property_type"]
        property.gender_preference = request.form["gender_preference"]

        property.monthly_rent = request.form["monthly_rent"]
        property.security_deposit = request.form["security_deposit"] or 0

        property.available_rooms = request.form["available_rooms"]

        property.city = request.form["city"]
        property.area = request.form["area"]
        property.address = request.form["address"]
        property.pincode = request.form["pincode"]

        property.description = request.form["description"]

        db.session.commit()

        flash("Property updated successfully!", "success")

        return redirect(url_for(
            "owner.my_properties"
        ))

    # Display edit page
    return render_template(
        "owner/edit_property.html",
        property=property
    )

@owner.route("/owner/property/<int:property_id>/delete", methods=["POST"])
def delete_property(property_id):

    if "user_id" not in session or session["role"] != "Owner":
        return redirect(url_for("auth.login"))

    property = Property.query.filter_by(
        property_id=property_id,
        owner_id=session["user_id"]
    ).first_or_404()

    db.session.delete(property)
    db.session.commit()

    flash("Property deleted successfully!", "success")

    return redirect(url_for("owner.my_properties"))

@owner.route("/owner/reviews")
def reviews():

    if "user_id" not in session or session["role"] != "Owner":
        return redirect(url_for("auth.login"))

    # Get properties belonging to this owner
    properties = Property.query.filter_by(
        owner_id=session["user_id"]
    ).all()

    property_ids = [
        property.property_id
        for property in properties
    ]

    # Get reviews for owner's properties
    if property_ids:

        reviews = Review.query.filter(
            Review.property_id.in_(property_ids)
        ).order_by(
            Review.review_date.desc()
        ).all()

    else:

        reviews = []

    # Calculate average rating
    if reviews:

        average_rating = round(
            sum(review.rating for review in reviews) / len(reviews),
            1
        )

    else:

        average_rating = 0

    return render_template(
        "owner/reviews.html",
        reviews=reviews,
        average_rating=average_rating,
        total_reviews=len(reviews)
    )
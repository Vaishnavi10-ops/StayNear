from flask import Blueprint, redirect, render_template, request, url_for
from datetime import datetime
from database.db import db

from models.user import User
from models.owner import Owner
from models.property import Property
from models.booking import Booking
from models.review import Review


# ==========================================
# ADMIN BLUEPRINT
# ==========================================

admin = Blueprint("admin", __name__)


# ==========================================
# ADMIN DASHBOARD
# ==========================================

@admin.route("/admin/dashboard")
def admin_dashboard():

    # ==========================================
    # SELECTED MONTH
    # ==========================================

    month = request.args.get(
        "month",
        datetime.now().strftime("%Y-%m")
    )

    try:

        selected_date = datetime.strptime(
            month,
            "%Y-%m"
        )

    except ValueError:

        selected_date = datetime.now()
        month = selected_date.strftime("%Y-%m")


    # ==========================================
    # DATE RANGE
    # ==========================================

    start_date = selected_date.replace(
        day=1,
        hour=0,
        minute=0,
        second=0,
        microsecond=0
    )


    # First day of next month

    if selected_date.month == 12:

        next_month = selected_date.replace(
            year=selected_date.year + 1,
            month=1,
            day=1
        )

    else:

        next_month = selected_date.replace(
            month=selected_date.month + 1,
            day=1
        )


    # ==========================================
    # BASIC STATISTICS
    # ==========================================

    total_users = User.query.filter(
        User.created_at >= start_date,
        User.created_at < next_month
    ).count()


    total_owners = Owner.query.filter(
        Owner.created_at >= start_date,
        Owner.created_at < next_month
    ).count()


    total_properties = Property.query.filter(
        Property.created_at >= start_date,
        Property.created_at < next_month
    ).count()


    pending_properties = Property.query.filter(
        Property.created_at >= start_date,
        Property.created_at < next_month,
        Property.property_status == "Pending"
    ).count()


    total_bookings = Booking.query.filter(
        Booking.created_at >= start_date,
        Booking.created_at < next_month
    ).count()


    # ==========================================
    # BOOKING STATUS ANALYSIS
    # ==========================================

    pending_bookings = Booking.query.filter(
        Booking.created_at >= start_date,
        Booking.created_at < next_month,
        Booking.booking_status == "Pending"
    ).count()


    approved_bookings = Booking.query.filter(
        Booking.created_at >= start_date,
        Booking.created_at < next_month,
        Booking.booking_status == "Approved"
    ).count()


    rejected_bookings = Booking.query.filter(
        Booking.created_at >= start_date,
        Booking.created_at < next_month,
        Booking.booking_status == "Rejected"
    ).count()


    completed_bookings = Booking.query.filter(
        Booking.created_at >= start_date,
        Booking.created_at < next_month,
        Booking.booking_status == "Completed"
    ).count()


    # ==========================================
    # PROPERTY STATUS ANALYSIS
    # ==========================================

    approved_properties = Property.query.filter(
        Property.created_at >= start_date,
        Property.created_at < next_month,
        Property.property_status == "Approved"
    ).count()


    rejected_properties = Property.query.filter(
        Property.created_at >= start_date,
        Property.created_at < next_month,
        Property.property_status == "Rejected"
    ).count()


    # ==========================================
    # PROPERTY TYPE ANALYSIS
    # ==========================================

    hostel_properties = Property.query.filter(
        Property.created_at >= start_date,
        Property.created_at < next_month,
        Property.property_type == "Hostel"
    ).count()


    pg_properties = Property.query.filter(
        Property.created_at >= start_date,
        Property.created_at < next_month,
        Property.property_type == "PG"
    ).count()


    flat_properties = Property.query.filter(
        Property.created_at >= start_date,
        Property.created_at < next_month,
        Property.property_type == "Flat"
    ).count()


    room_properties = Property.query.filter(
        Property.created_at >= start_date,
        Property.created_at < next_month,
        Property.property_type == "Room"
    ).count()


    # ==========================================
    # RATINGS ANALYSIS
    # ==========================================

    ratings = Review.query.filter(
        Review.review_date >= start_date,
        Review.review_date < next_month
    ).all()


    if ratings:

        average_rating = round(
            sum(review.rating for review in ratings)
            / len(ratings),
            1
        )

    else:

        average_rating = 0


    total_ratings = len(ratings)


    # ==========================================
    # RENDER DASHBOARD
    # ==========================================

    return render_template(
        "admin/dashboard.html",

        total_users=total_users,
        total_owners=total_owners,
        total_properties=total_properties,
        pending_properties=pending_properties,
        total_bookings=total_bookings,

        pending_bookings=pending_bookings,
        approved_bookings=approved_bookings,
        rejected_bookings=rejected_bookings,
        completed_bookings=completed_bookings,

        approved_properties=approved_properties,
        rejected_properties=rejected_properties,

        hostel_properties=hostel_properties,
        pg_properties=pg_properties,
        flat_properties=flat_properties,
        room_properties=room_properties,

        average_rating=average_rating,
        total_ratings=total_ratings,

        selected_month=month
    )


# ==========================================
# MANAGE PROPERTIES
# ==========================================

@admin.route("/admin/properties")
def manage_properties():

    search = request.args.get(
        "search",
        ""
    ).strip()

    status = request.args.get(
        "status",
        "All"
    )


    query = Property.query


    # ==========================================
    # SEARCH
    # ==========================================

    if search:

        search_term = f"%{search}%"

        query = query.filter(
            db.or_(
                Property.property_name.ilike(search_term),
                Property.city.ilike(search_term),
                Property.address.ilike(search_term)
            )
        )


    # ==========================================
    # STATUS FILTER
    # ==========================================

    if status and status != "All":

        query = query.filter(
            Property.property_status == status
        )


    # ==========================================
    # GET PROPERTIES
    # ==========================================

    properties = query.order_by(
        Property.created_at.desc()
    ).all()


    # ==========================================
    # GET OWNER FOR EACH PROPERTY
    # ==========================================

    property_owners = {}

    for property in properties:

        owner = Owner.query.filter_by(
            owner_id=property.owner_id
        ).first()

        property_owners[property.property_id] = owner


    # ==========================================
    # RENDER PROPERTIES PAGE
    # ==========================================

    return render_template(
        "admin/properties.html",

        properties=properties,
        property_owners=property_owners,

        search=search,
        status=status
    )


# ==========================================
# APPROVE PROPERTY
# ==========================================

@admin.route(
    "/admin/properties/<int:property_id>/approve",
    methods=["POST"]
)
def approve_property(property_id):

    property = Property.query.get_or_404(
        property_id
    )

    property.property_status = "Approved"

    db.session.commit()

    return redirect(
        url_for("admin.manage_properties")
    )


# ==========================================
# REJECT PROPERTY
# ==========================================

@admin.route(
    "/admin/properties/<int:property_id>/reject",
    methods=["POST"]
)
def reject_property(property_id):

    property = Property.query.get_or_404(
        property_id
    )

    property.property_status = "Rejected"

    db.session.commit()

    return redirect(
        url_for("admin.manage_properties")
    )
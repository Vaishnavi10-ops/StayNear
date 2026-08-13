from flask import Blueprint, redirect, render_template, request, url_for, session, flash
from database.db import db

from models.user import User
from models.owner import Owner
from models.property import Property
from models.booking import Booking
from models.review import Review


# =========================================================
# ADMIN BLUEPRINT
# =========================================================

admin = Blueprint("admin", __name__)


# =========================================================
# ADMIN ACCESS CHECK
# =========================================================

def admin_required():

    if "user_id" not in session:
        return False

    if session.get("role") != "Admin":
        return False

    return True


# =========================================================
# ADMIN DASHBOARD
# =========================================================

@admin.route("/admin/dashboard")
def admin_dashboard():

    # -----------------------------------------------------
    # SECURITY
    # -----------------------------------------------------

    if not admin_required():
        return redirect(url_for("auth.login"))


    # =====================================================
    # MONTH FILTER
    # =====================================================

    from datetime import datetime, timedelta
    from sqlalchemy import and_

    selected_month = request.args.get("month")


    # -----------------------------------------------------
    # DEFAULT MONTH
    # -----------------------------------------------------

    if not selected_month:

        selected_month = datetime.now().strftime("%Y-%m")


    # -----------------------------------------------------
    # CREATE MONTH DATE RANGE
    # -----------------------------------------------------

    try:

        month_start = datetime.strptime(
            selected_month + "-01",
            "%Y-%m-%d"
        )

        if month_start.month == 12:

            next_month = datetime(
                month_start.year + 1,
                1,
                1
            )

        else:

            next_month = datetime(
                month_start.year,
                month_start.month + 1,
                1
            )

    except ValueError:

        selected_month = datetime.now().strftime("%Y-%m")

        month_start = datetime.strptime(
            selected_month + "-01",
            "%Y-%m-%d"
        )

        if month_start.month == 12:

            next_month = datetime(
                month_start.year + 1,
                1,
                1
            )

        else:

            next_month = datetime(
                month_start.year,
                month_start.month + 1,
                1
            )


    # =====================================================
    # USER STATISTICS
    # =====================================================

    total_users = User.query.filter(
        User.created_at >= month_start,
        User.created_at < next_month
    ).count()


    total_owners = Owner.query.filter(
        Owner.created_at >= month_start,
        Owner.created_at < next_month
    ).count()


    # =====================================================
    # PROPERTY STATISTICS
    # =====================================================

    total_properties = Property.query.filter(
        Property.created_at >= month_start,
        Property.created_at < next_month
    ).count()


    approved_properties = Property.query.filter(
        Property.property_status == "Approved",
        Property.created_at >= month_start,
        Property.created_at < next_month
    ).count()


    pending_properties = Property.query.filter(
        Property.property_status == "Pending",
        Property.created_at >= month_start,
        Property.created_at < next_month
    ).count()


    rejected_properties = Property.query.filter(
        Property.property_status == "Rejected",
        Property.created_at >= month_start,
        Property.created_at < next_month
    ).count()


    # =====================================================
    # AVAILABLE / UNAVAILABLE PROPERTIES
    # =====================================================

    available_properties = Property.query.filter(
        Property.available == True,
        Property.created_at >= month_start,
        Property.created_at < next_month
    ).count()


    unavailable_properties = Property.query.filter(
        Property.available == False,
        Property.created_at >= month_start,
        Property.created_at < next_month
    ).count()


    # =====================================================
    # PROPERTY TYPE STATISTICS
    # =====================================================

    hostel_properties = Property.query.filter(
        Property.property_type == "Hostel",
        Property.created_at >= month_start,
        Property.created_at < next_month
    ).count()


    pg_properties = Property.query.filter(
        Property.property_type == "PG",
        Property.created_at >= month_start,
        Property.created_at < next_month
    ).count()


    room_properties = Property.query.filter(
        Property.property_type == "Room",
        Property.created_at >= month_start,
        Property.created_at < next_month
    ).count()


    flat_properties = Property.query.filter(
        Property.property_type == "Flat",
        Property.created_at >= month_start,
        Property.created_at < next_month
    ).count()


    apartment_properties = Property.query.filter(
        Property.property_type == "Apartment",
        Property.created_at >= month_start,
        Property.created_at < next_month
    ).count()


    # =====================================================
    # BOOKING STATISTICS
    # =====================================================

    total_bookings = Booking.query.filter(
        Booking.created_at >= month_start,
        Booking.created_at < next_month
    ).count()


    pending_bookings = Booking.query.filter(
        Booking.booking_status == "Pending",
        Booking.created_at >= month_start,
        Booking.created_at < next_month
    ).count()


    approved_bookings = Booking.query.filter(
        Booking.booking_status == "Approved",
        Booking.created_at >= month_start,
        Booking.created_at < next_month
    ).count()


    rejected_bookings = Booking.query.filter(
        Booking.booking_status == "Rejected",
        Booking.created_at >= month_start,
        Booking.created_at < next_month
    ).count()


    completed_bookings = Booking.query.filter(
        Booking.booking_status == "Completed",
        Booking.created_at >= month_start,
        Booking.created_at < next_month
    ).count()


    cancelled_bookings = Booking.query.filter(
        Booking.booking_status == "Cancelled",
        Booking.created_at >= month_start,
        Booking.created_at < next_month
    ).count()


    # =====================================================
    # REVIEW / RATING STATISTICS
    # =====================================================

    # Review model does not have created_at,
    # so ratings are calculated from all existing reviews.

    ratings = Review.query.all()

    total_ratings = len(ratings)


    if ratings:

        average_rating = round(
            sum(
                float(review.rating)
                for review in ratings
            ) / len(ratings),
            1
        )

    else:

        average_rating = 0


    # =====================================================
    # RECENT PROPERTIES
    # =====================================================

    recent_properties = Property.query.filter(
        Property.created_at >= month_start,
        Property.created_at < next_month
    ).order_by(
        Property.created_at.desc()
    ).limit(5).all()


    # =====================================================
    # RECENT BOOKINGS
    # =====================================================

    recent_bookings = Booking.query.filter(
        Booking.created_at >= month_start,
        Booking.created_at < next_month
    ).order_by(
        Booking.created_at.desc()
    ).limit(5).all()


    # =====================================================
    # RECENT USERS
    # =====================================================

    recent_users = User.query.filter(
        User.created_at >= month_start,
        User.created_at < next_month
    ).order_by(
        User.created_at.desc()
    ).limit(5).all()


    # =====================================================
    # DASHBOARD
    # =====================================================

    return render_template(
        "admin/dashboard.html",

        # Selected month
        selected_month=selected_month,

        # Users
        total_users=total_users,
        total_owners=total_owners,

        # Properties
        total_properties=total_properties,
        approved_properties=approved_properties,
        pending_properties=pending_properties,
        rejected_properties=rejected_properties,

        available_properties=available_properties,
        unavailable_properties=unavailable_properties,

        # Property types
        hostel_properties=hostel_properties,
        pg_properties=pg_properties,
        room_properties=room_properties,
        flat_properties=flat_properties,
        apartment_properties=apartment_properties,

        # Bookings
        total_bookings=total_bookings,
        pending_bookings=pending_bookings,
        approved_bookings=approved_bookings,
        rejected_bookings=rejected_bookings,
        completed_bookings=completed_bookings,
        cancelled_bookings=cancelled_bookings,

        # Ratings
        total_ratings=total_ratings,
        average_rating=average_rating,

        # Recent data
        recent_properties=recent_properties,
        recent_bookings=recent_bookings,
        recent_users=recent_users
    )


# =========================================================
# MANAGE PROPERTIES
# =========================================================

@admin.route("/admin/properties")
def manage_properties():

    if not admin_required():
        return redirect(url_for("auth.login"))


    # =====================================================
    # SEARCH
    # =====================================================

    search = request.args.get(
        "search",
        ""
    ).strip()


    # =====================================================
    # STATUS
    # =====================================================

    status = request.args.get(
        "status",
        "All"
    )


    # =====================================================
    # PROPERTY TYPE
    # =====================================================

    property_type = request.args.get(
        "property_type",
        "All"
    )


    # =====================================================
    # BASE QUERY
    # =====================================================

    query = Property.query


    # =====================================================
    # SEARCH FILTER
    # =====================================================

    if search:

        search_term = f"%{search}%"

        query = query.filter(
            db.or_(
                Property.property_name.ilike(
                    search_term
                ),
                Property.city.ilike(
                    search_term
                ),
                Property.area.ilike(
                    search_term
                ),
                Property.address.ilike(
                    search_term
                )
            )
        )


    # =====================================================
    # STATUS FILTER
    # =====================================================

    if status != "All":

        query = query.filter(
            Property.property_status == status
        )


    # =====================================================
    # PROPERTY TYPE FILTER
    # =====================================================

    if property_type != "All":

        query = query.filter(
            Property.property_type == property_type
        )


    # =====================================================
    # GET PROPERTIES
    # =====================================================

    properties = query.order_by(
        Property.created_at.desc()
    ).all()


    # =====================================================
    # GET OWNERS
    # =====================================================

    property_owners = {}

    for property in properties:

        owner = Owner.query.filter_by(
            owner_id=property.owner_id
        ).first()

        property_owners[
            property.property_id
        ] = owner


    # =====================================================
    # RENDER
    # =====================================================

    return render_template(
        "admin/properties.html",

        properties=properties,

        property_owners=property_owners,

        search=search,

        status=status,

        property_type=property_type
    )


@admin.route("/admin/property/<int:property_id>")
def view_property(property_id):

    # -----------------------------------------------------
    # SECURITY
    # -----------------------------------------------------

    if not admin_required():
        return redirect(url_for("auth.login"))


    # -----------------------------------------------------
    # GET PROPERTY
    # -----------------------------------------------------

    property = Property.query.get_or_404(property_id)


    # -----------------------------------------------------
    # GET OWNER
    # -----------------------------------------------------

    owner = Owner.query.filter_by(
        owner_id=property.owner_id
    ).first()


    # -----------------------------------------------------
    # DISPLAY DETAILS
    # -----------------------------------------------------

    return render_template(
        "admin/property_details.html",

        property=property,

        owner=owner
    )


# =========================================================
# APPROVE PROPERTY
# =========================================================

@admin.route(
    "/admin/properties/<int:property_id>/approve",
    methods=["POST"]
)
def approve_property(property_id):

    if not admin_required():
        return redirect(url_for("auth.login"))


    property = Property.query.get_or_404(
        property_id
    )


    property.property_status = "Approved"


    db.session.commit()


    flash(
        "Property approved successfully.",
        "success"
    )


    return redirect(
        url_for(
            "admin.manage_properties"
        )
    )


# =========================================================
# REJECT PROPERTY
# =========================================================

@admin.route(
    "/admin/properties/<int:property_id>/reject",
    methods=["POST"]
)
def reject_property(property_id):

    if not admin_required():
        return redirect(url_for("auth.login"))


    property = Property.query.get_or_404(
        property_id
    )


    property.property_status = "Rejected"


    db.session.commit()


    flash(
        "Property rejected successfully.",
        "warning"
    )


    return redirect(
        url_for(
            "admin.manage_properties"
        )
    )


# =========================================================
# SET PROPERTY TO PENDING
# =========================================================

@admin.route(
    "/admin/properties/<int:property_id>/pending",
    methods=["POST"]
)
def pending_property(property_id):

    if not admin_required():
        return redirect(url_for("auth.login"))


    property = Property.query.get_or_404(
        property_id
    )


    property.property_status = "Pending"


    db.session.commit()


    flash(
        "Property moved to pending.",
        "info"
    )


    return redirect(
        url_for(
            "admin.manage_properties"
        )
    )

@admin.route("/admin/users")
def manage_users():

    # -----------------------------------------------------
    # SECURITY
    # -----------------------------------------------------

    if not admin_required():
        return redirect(url_for("auth.login"))


    # -----------------------------------------------------
    # SEARCH
    # -----------------------------------------------------

    search = request.args.get("search", "").strip()


    # -----------------------------------------------------
    # USERS QUERY
    # -----------------------------------------------------

    query = User.query


    if search:

        search_pattern = f"%{search}%"

        query = query.filter(
            db.or_(
                User.full_name.ilike(search_pattern),
                User.email.ilike(search_pattern),
                User.phone.ilike(search_pattern)
            )
        )


    # -----------------------------------------------------
    # GET USERS
    # -----------------------------------------------------

    users = query.order_by(
        User.created_at.desc()
    ).all()


    # -----------------------------------------------------
    # DASHBOARD DATA
    # -----------------------------------------------------

    total_users = User.query.count()


    # -----------------------------------------------------
    # RENDER
    # -----------------------------------------------------

    return render_template(
        "admin/users.html",

        users=users,

        total_users=total_users,

        search=search
    )

@admin.route("/admin/users/<int:user_id>")
def view_user(user_id):

    # -----------------------------------------------------
    # SECURITY
    # -----------------------------------------------------

    if not admin_required():
        return redirect(url_for("auth.login"))


    # -----------------------------------------------------
    # GET USER
    # -----------------------------------------------------

    user = User.query.get_or_404(user_id)


    # -----------------------------------------------------
    # RENDER
    # -----------------------------------------------------

    return render_template(
        "admin/user_details.html",
        user=user
    )

@admin.route("/admin/owners")
def manage_owners():

    if not admin_required():
        return redirect(url_for("auth.login"))

    search = request.args.get("search", "").strip()

    query = Owner.query

    if search:

        query = query.filter(
            db.or_(
                Owner.full_name.ilike(f"%{search}%"),
                Owner.email.ilike(f"%{search}%"),
                Owner.phone.ilike(f"%{search}%")
            )
        )

    owners = query.order_by(
        Owner.created_at.desc()
    ).all()


    # -----------------------------------------
    # PROPERTY COUNT FOR EACH OWNER
    # -----------------------------------------

    owner_property_counts = {}

    for owner in owners:

        owner_property_counts[owner.owner_id] = Property.query.filter_by(
            owner_id=owner.owner_id
        ).count()


    return render_template(
        "admin/owners.html",

        owners=owners,

        search=search,

        owner_property_counts=owner_property_counts
    )

@admin.route("/admin/owners/<int:owner_id>")
def view_owner(owner_id):

    if not admin_required():
        return redirect(url_for("auth.login"))

    # Find owner
    owner = Owner.query.get_or_404(owner_id)

    # Find all properties belonging to this owner
    properties = Property.query.filter_by(
        owner_id=owner.owner_id
    ).order_by(
        Property.created_at.desc()
    ).all()

    return render_template(
        "admin/owner_details.html",
        owner=owner,
        properties=properties
    )

# =====================================================
# MANAGE BOOKINGS
# =====================================================

@admin.route("/admin/bookings")
def manage_bookings():

    # -------------------------------------------------
    # SECURITY
    # -------------------------------------------------

    if not admin_required():
        return redirect(url_for("auth.login"))


    # -------------------------------------------------
    # SEARCH & FILTER
    # -------------------------------------------------

    search = request.args.get("search", "").strip()

    status = request.args.get(
        "status",
        "All"
    )


    # -------------------------------------------------
    # BASE QUERY
    # -------------------------------------------------

    query = Booking.query


    # -------------------------------------------------
    # STATUS FILTER
    # -------------------------------------------------

    if status != "All":

        query = query.filter(
            Booking.booking_status == status
        )


    # -------------------------------------------------
    # SEARCH
    # -------------------------------------------------

    if search:

        search_pattern = f"%{search}%"

        query = query.join(
            User
        ).join(
            Property
        ).filter(

            db.or_(

                User.full_name.ilike(
                    search_pattern
                ),

                User.email.ilike(
                    search_pattern
                ),

                Property.property_name.ilike(
                    search_pattern
                ),

                Property.city.ilike(
                    search_pattern
                )

            )
        )


    # -------------------------------------------------
    # BOOKINGS
    # -------------------------------------------------

    bookings = query.order_by(
        Booking.created_at.desc()
    ).all()


    # -------------------------------------------------
    # RENDER
    # -------------------------------------------------

    return render_template(
        "admin/bookings.html",

        bookings=bookings,

        search=search,

        status=status
    )

# =====================================================
# VIEW BOOKING
# =====================================================

@admin.route("/admin/bookings/<int:booking_id>")
def view_booking(booking_id):

    # -------------------------------------------------
    # SECURITY
    # -------------------------------------------------

    if not admin_required():
        return redirect(url_for("auth.login"))


    # -------------------------------------------------
    # GET BOOKING
    # -------------------------------------------------

    booking = Booking.query.get_or_404(
        booking_id
    )


    # -------------------------------------------------
    # OWNER
    # -------------------------------------------------

    owner = None

    if booking.property:

        owner = Owner.query.get(
            booking.property.owner_id
        )


    # -------------------------------------------------
    # RENDER
    # -------------------------------------------------

    return render_template(
        "admin/booking_details.html",

        booking=booking,

        owner=owner
    )

# =========================================================
# MANAGE REVIEWS
# =========================================================

@admin.route("/admin/reviews")
def manage_reviews():

    # -----------------------------------------------------
    # SECURITY
    # -----------------------------------------------------

    if not admin_required():
        return redirect(url_for("auth.login"))


    # -----------------------------------------------------
    # FILTER VALUES
    # -----------------------------------------------------

    search = request.args.get("search", "").strip()
    rating = request.args.get("rating", "All").strip()


    # -----------------------------------------------------
    # BASE QUERY
    # -----------------------------------------------------

    query = Review.query


    # -----------------------------------------------------
    # SEARCH
    # -----------------------------------------------------

    if search:

        search_term = f"%{search}%"

        query = (
            query
            .join(Review.user)
            .join(Review.property)
            .filter(
                db.or_(
                    User.full_name.ilike(search_term),
                    User.email.ilike(search_term),
                    Property.property_name.ilike(search_term),
                    Property.city.ilike(search_term)
                )
            )
        )


    # -----------------------------------------------------
    # RATING FILTER
    # -----------------------------------------------------

    if rating != "All":

        try:

            rating_value = int(rating)

            if 1 <= rating_value <= 5:

                query = query.filter(
                    Review.rating == rating_value
                )

            else:

                rating = "All"

        except ValueError:

            rating = "All"


    # -----------------------------------------------------
    # GET REVIEWS
    # -----------------------------------------------------

    reviews = query.order_by(
        Review.review_date.desc()
    ).all()


    # -----------------------------------------------------
    # RENDER
    # -----------------------------------------------------

    return render_template(
        "admin/reviews.html",

        reviews=reviews,

        search=search,

        rating=rating
    )

# =========================================================
# VIEW REVIEW DETAILS
# =========================================================

@admin.route("/admin/reviews/<int:review_id>")
def view_review(review_id):

    # -----------------------------------------------------
    # SECURITY
    # -----------------------------------------------------

    if not admin_required():
        return redirect(url_for("auth.login"))


    # -----------------------------------------------------
    # FIND REVIEW
    # -----------------------------------------------------

    review = Review.query.get_or_404(review_id)


    # -----------------------------------------------------
    # RENDER
    # -----------------------------------------------------

    return render_template(
        "admin/review_details.html",
        review=review
    )
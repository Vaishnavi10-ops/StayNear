from flask import Blueprint, render_template

owner = Blueprint("owner", __name__)

@owner.route("/owner/dashboard")
def dashboard():

    total_properties = 0
    approved_properties = 0
    pending_properties = 0
    total_bookings = 0

    return render_template(
        "owner/dashboard.html",
        total_properties=total_properties,
        approved_properties=approved_properties,
        pending_properties=pending_properties,
        total_bookings=total_bookings
    )
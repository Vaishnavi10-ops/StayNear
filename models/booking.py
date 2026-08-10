from database.db import db


class Booking(db.Model):

    __tablename__ = "bookings"

    booking_id = db.Column(
        db.Integer,
        primary_key=True,
        autoincrement=True
    )

    property_id = db.Column(
        db.Integer,
        db.ForeignKey("properties.property_id"),
        nullable=False
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.user_id"),
        nullable=False
    )

    visit_date = db.Column(
        db.Date,
        nullable=False
    )

    visit_time = db.Column(
        db.Time,
        nullable=False
    )

    message = db.Column(
        db.Text
    )

    booking_status = db.Column(
        db.Enum(
            "Pending",
            "Approved",
            "Rejected",
            "Completed",
            "Cancelled"
        ),
        default="Pending"
    )

    created_at = db.Column(
        db.DateTime,
        server_default=db.func.current_timestamp()
    )

    property = db.relationship(
        "Property",
        backref=db.backref("bookings", lazy=True)
    )

    user = db.relationship(
        "User",
        backref=db.backref("bookings", lazy=True)
    )
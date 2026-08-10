from database.db import db


class Review(db.Model):

    __tablename__ = "reviews"

    review_id = db.Column(
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

    rating = db.Column(
        db.Integer,
        nullable=False
    )

    review_date = db.Column(
        db.DateTime,
        server_default=db.func.current_timestamp()
    )

    user = db.relationship(
        "User",
        backref=db.backref("reviews", lazy=True)
    )

    property = db.relationship(
        "Property",
        backref=db.backref("reviews", lazy=True)
    )
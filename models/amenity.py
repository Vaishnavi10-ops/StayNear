from database.db import db


class Amenity(db.Model):

    __tablename__ = "amenities"

    amenity_id = db.Column(
        db.Integer,
        primary_key=True
    )

    amenity_name = db.Column(
        db.String(100),
        nullable=False
    )
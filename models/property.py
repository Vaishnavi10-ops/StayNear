from database.db import db

class Property(db.Model):

    __tablename__ = "properties"

    property_id = db.Column(db.Integer, primary_key=True)

    owner_id = db.Column(
        db.Integer,
        db.ForeignKey("owners.owner_id", ondelete="CASCADE"),
        nullable=False
    )

    property_name = db.Column(db.String(150), nullable=False)

    property_type = db.Column(
        db.Enum("Hostel", "PG", "Flat", "Room", "Apartment"),
        nullable=False
    )

    address = db.Column(db.Text, nullable=False)

    city = db.Column(db.String(100), nullable=False)

    pincode = db.Column(db.String(10))

    latitude = db.Column(db.Numeric(10, 8))

    longitude = db.Column(db.Numeric(11, 8))

    monthly_rent = db.Column(db.Numeric(10, 2), nullable=False)

    security_deposit = db.Column(db.Numeric(10, 2), default=0)

    available_rooms = db.Column(db.Integer, default=1)

    description = db.Column(db.Text)

    available = db.Column(db.Boolean, default=True)

    property_status = db.Column(
        db.Enum("Pending", "Approved", "Rejected"),
        default="Pending"
    )

    created_at = db.Column(
        db.DateTime,
        server_default=db.func.current_timestamp()
    )

    images = db.relationship(
        "PropertyImage",
        backref="property",
        cascade="all, delete-orphan"
    )
    gender_preference = db.Column(
    db.Enum("Boys", "Girls", "Co-ed"),
    nullable=False
    )
    area = db.Column(db.String(100), nullable=False)
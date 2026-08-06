from models.user import User
from models.owner import Owner
from database.db import db

from werkzeug.security import generate_password_hash
from werkzeug.security import check_password_hash


def register_account(full_name, email, phone, password, confirm_password, role):

    # Check password confirmation
    if password != confirm_password:
        return False, "Passwords do not match."

    # Check duplicate email
    if User.query.filter_by(email=email).first() or Owner.query.filter_by(email=email).first():
        return False, "Email already exists."

    # Check duplicate phone
    if User.query.filter_by(phone=phone).first() or Owner.query.filter_by(phone=phone).first():
        return False, "Phone number already exists."

    # Hash password
    hashed_password = generate_password_hash(password)

    # Create account
    if role == "User":

        account = User(
            full_name=full_name,
            email=email,
            phone=phone,
            password=hashed_password
        )

    else:

        account = Owner(
            full_name=full_name,
            email=email,
            phone=phone,
            password=hashed_password
        )

    db.session.add(account)
    db.session.commit()

    return True, "Registration Successful!"

def login_account(email, password, role):

    # Check role and find account
    if role == "User":
        account = User.query.filter_by(email=email).first()

    elif role == "Owner":
        account = Owner.query.filter_by(email=email).first()

    else:
        # Temporary Admin Login
        if email == "admin@staynear.com" and password == "admin123":
            return True, {
                "id": 1,
                "name": "Administrator",
                "role": "Admin"
            }

        return False, "Invalid Admin Credentials"

    # Account not found
    if account is None:
        return False, "Account does not exist."

    # Verify password
    if not check_password_hash(account.password, password):
        return False, "Incorrect password."

    return True, {
        "id": account.user_id if role == "User" else account.owner_id,
        "name": account.full_name,
        "role": role
    }
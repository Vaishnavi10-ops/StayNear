from models.user import User
from models.owner import Owner
from database.db import db

from werkzeug.security import generate_password_hash
from werkzeug.security import check_password_hash
from sqlalchemy import text


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

    # =========================
    # ADMIN LOGIN
    # =========================

    if role == "Admin":

        result = db.session.execute(
            text("""
                SELECT admin_id, username, password
                FROM admins
                WHERE username = :username
                LIMIT 1
            """),
            {
                "username": email
            }
        ).fetchone()

        if result is None:
            return False, "Admin account does not exist."

        if result.password != password:
            return False, "Incorrect admin password."

        return True, {
            "id": result.admin_id,
            "name": "Administrator",
            "role": "Admin"
        }


    # =========================
    # USER LOGIN
    # =========================

    if role == "User":

        account = User.query.filter_by(
            email=email
        ).first()


    # =========================
    # OWNER LOGIN
    # =========================

    elif role == "Owner":

        account = Owner.query.filter_by(
            email=email
        ).first()


    else:

        return False, "Invalid role."


    # =========================
    # ACCOUNT NOT FOUND
    # =========================

    if account is None:
        return False, "Account does not exist."


    # =========================
    # PASSWORD CHECK
    # =========================

    if not check_password_hash(
        account.password,
        password
    ):
        return False, "Incorrect password."


    # =========================
    # SUCCESS
    # =========================

    return True, {
        "id": (
            account.user_id
            if role == "User"
            else account.owner_id
        ),
        "name": account.full_name,
        "role": role
    }
from unittest import result

from flask import Blueprint, render_template, request, redirect, url_for, flash

from models.user import User
from services.authentication import register_account
from flask import session
from services.authentication import login_account
from werkzeug.security import check_password_hash


auth = Blueprint("auth", __name__)

from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from services.authentication import login_account

auth = Blueprint("auth", __name__)

@auth.route('/login', methods=['GET', 'POST'])
def login():

    if request.method == "POST":

        email = request.form["email"]
        password = request.form["password"]
        role = request.form["role"]

        success, result = login_account(email, password, role)

        if success:

            session["user_id"] = result["id"]
            session["role"] = result["role"]
            session["name"] = result["name"]

            if result["role"] == "Admin":
                return redirect(url_for("admin.dashboard"))

            elif result["role"] == "Owner":
                return redirect(url_for("owner.dashboard"))






            else:
                return redirect(url_for("user.home"))

        flash(result, "danger")

    return render_template("auth/login.html")


@auth.route('/register', methods=['GET', 'POST'])
def register():

    if request.method == "POST":

        full_name = request.form["full_name"]
        email = request.form["email"]
        phone = request.form["phone"]
        password = request.form["password"]
        confirm_password = request.form["confirm_password"]
        role = request.form["role"]

        success, message = register_account(
            full_name,
            email,
            phone,
            password,
            confirm_password,
            role
        )

        flash(message)

        if success:
            return redirect(url_for("auth.login"))

    return render_template("auth/register.html")


@auth.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("auth.login"))
from flask import Blueprint, render_template

user = Blueprint("user", __name__)

@user.route("/user/dashboard")
def user_dashboard():
    return render_template("user/dashboard.html")
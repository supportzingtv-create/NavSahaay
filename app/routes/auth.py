from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user
from app.models import User

auth_bp=Blueprint("auth",__name__)

@auth_bp.route("/login", methods=["GET","POST"])
def login():
    if request.method=="POST":
        user=User.get_by_email(request.form["email"])
        if user and user.active and user.check_password(request.form["password"]):
            login_user(user)
            return redirect(url_for("admin.dashboard", _external=True))
        flash("Invalid email or password.", "error")
    return render_template("login.html")

@auth_bp.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("main.home"))

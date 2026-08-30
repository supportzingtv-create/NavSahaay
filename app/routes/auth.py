from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user
from app.models import User

auth_bp=Blueprint("auth",__name__)

@auth_bp.route("/login", methods=["GET","POST"])
def login():
    if request.method=="POST":
        email = request.form["email"]
        password = request.form["password"]

        user = User.get_by_email(email)

        # If user not found, try to run seeding once to ensure admin exists
        if not user:
            from app.services.seed import seed_admin_and_events
            seed_admin_and_events()
            user = User.get_by_email(email)

        if user and user.active and user.check_password(password):
            login_user(user)
            # Use absolute URL to ensure we stay on the correct subdomain
            return redirect(url_for("admin.dashboard", _external=True))

        flash("Invalid email or password.", "error")
    return render_template("login.html")

@auth_bp.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("main.home", _external=True))

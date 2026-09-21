from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, current_user
from app.models import User

auth_bp=Blueprint("auth",__name__)

@auth_bp.route("/login", methods=["GET","POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("admin.dashboard"))
    if request.method=="POST":
        email = request.form["email"].strip().lower()
        password = request.form["password"].strip()

        # Always run seed_admin_and_events on login attempt to ensure
        # credentials in Firestore perfectly sync with Vercel Environment Variables
        try:
            from app.services.seed import seed_admin_and_events
            seed_admin_and_events()
        except Exception as e:
            print(f"Login seeding failed: {e}")

        user = User.get_by_email(email)

        if user and user.active and user.check_password(password):
            login_user(user)
            return redirect(url_for("admin.dashboard"))

        flash("Invalid email or password.", "error")
    return render_template("login.html")

@auth_bp.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("main.home"))

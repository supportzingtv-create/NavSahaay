from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user
from app.models import User

auth_bp=Blueprint("auth",__name__)

@auth_bp.route("/login", methods=["GET","POST"])
def login():
    return redirect(url_for("admin.dashboard"))

@auth_bp.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("main.home"))

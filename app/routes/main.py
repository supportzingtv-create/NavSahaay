from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from datetime import datetime
from app import db
from app.models import Donation, Volunteer, Event, Contact
import secrets

main_bp = Blueprint("main", __name__)

@main_bp.route("/")
def home():
    events = Event.query.filter_by(active=True).order_by(Event.event_date.asc()).limit(3).all()
    return render_template("home.html", events=events)

@main_bp.route("/donate", methods=["POST"])
def donate():
    try:
        amount = float(request.form["amount"])
        if amount < 100: raise ValueError()
    except (KeyError, ValueError):
        flash("Please enter a valid donation amount of at least ₹100.", "error")
        return redirect(url_for("main.home") + "#donate")
    donation = Donation(
        donation_id="SHV-" + secrets.token_hex(5).upper(),
        donor_name=request.form["donor_name"], email=request.form["email"],
        phone=request.form["phone"], address=request.form["address"],
        pan=request.form.get("pan"), amount=amount,
        frequency=request.form["frequency"], cause=request.form["cause"],
        anonymous=bool(request.form.get("anonymous")), status="PENDING"
    )
    db.session.add(donation); db.session.commit()
    flash(f"Donation request created: {donation.donation_id}. Payment is not connected in this local version.", "success")
    return redirect(url_for("main.home") + "#donate")

@main_bp.route("/volunteer", methods=["POST"])
def volunteer():
    age = int(request.form["age"])
    if age < 1:
        flash("Please enter a valid age.", "error")
        return redirect(url_for("main.home") + "#volunteer")
    v = Volunteer(reference_id="VOL-" + secrets.token_hex(5).upper(), name=request.form["name"],
                   email=request.form["email"], phone=request.form["phone"], city=request.form["city"],
                   age=age, interest=request.form["interest"], availability=request.form["availability"],
                   skills=request.form.get("skills"), experience=request.form.get("experience"),
                   source=request.form.get("source"))
    db.session.add(v); db.session.commit()
    flash(f"Volunteer registration received: {v.reference_id}", "success")
    return redirect(url_for("main.home") + "#volunteer")

@main_bp.route("/contact", methods=["POST"])
def contact():
    c=Contact(name=request.form["name"], email=request.form["email"], subject=request.form["subject"], message=request.form["message"])
    db.session.add(c); db.session.commit()
    flash("Your inquiry has been received.", "success")
    return redirect(url_for("main.home") + "#contact")

@main_bp.route("/events/<int:event_id>/register", methods=["POST"])
def event_register(event_id):
    from app.models import EventRegistration
    event = db.session.get(Event, event_id)
    if not event: return jsonify({"error":"Event not found"}), 404
    if event.capacity and len(event.registrations) >= event.capacity:
        return jsonify({"error":"Event capacity reached"}), 409
    r=EventRegistration(event_id=event.id,name=request.form["name"],email=request.form["email"],phone=request.form["phone"])
    db.session.add(r); db.session.commit()
    return jsonify({"message":"Registration successful"})

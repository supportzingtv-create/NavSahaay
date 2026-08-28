from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from datetime import datetime
from app.models import Donation, Volunteer, Event, Contact
import secrets

main_bp = Blueprint("main", __name__)

@main_bp.route("/")
def home():
    # Attempt to get events, but don't crash if DB is unavailable
    events = []
    try:
        all_events = Event.get_all(active_only=True)
        if all_events:
            events = all_events[:3]
    except Exception as e:
        print(f"Error fetching events: {e}")

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
    donation.save()
    flash(f"Donation request created: {donation.donation_id}.", "success")
    return redirect(url_for("main.home") + "#donate")

@main_bp.route("/volunteer", methods=["POST"])
def volunteer():
    try:
        age = int(request.form["age"])
        if age < 1: raise ValueError()
    except (KeyError, ValueError):
        flash("Please enter a valid age.", "error")
        return redirect(url_for("main.home") + "#volunteer")

    v = Volunteer(reference_id="VOL-" + secrets.token_hex(5).upper(), name=request.form["name"],
                   email=request.form["email"], phone=request.form["phone"], city=request.form["city"],
                   age=age, interest=request.form["interest"], availability=request.form["availability"],
                   skills=request.form.get("skills"), experience=request.form.get("experience"),
                   source=request.form.get("source"))
    v.save()
    flash(f"Volunteer registration received: {v.reference_id}", "success")
    return redirect(url_for("main.home") + "#volunteer")

@main_bp.route("/contact", methods=["POST"])
def contact():
    c=Contact(name=request.form["name"], email=request.form["email"], subject=request.form["subject"], message=request.form["message"])
    c.save()
    flash("Your inquiry has been received.", "success")
    return redirect(url_for("main.home") + "#contact")

@main_bp.route("/events/<string:event_id>/register", methods=["POST"])
def event_register(event_id):
    from app.models import EventRegistration
    event = Event.get_by_id(event_id)
    if not event: return jsonify({"error":"Event not found"}), 404

    regs = event.registrations
    if event.capacity and len(regs) >= event.capacity:
        return jsonify({"error":"Event capacity reached"}), 409

    r=EventRegistration(event_id=event.id,name=request.form["name"],email=request.form["email"],phone=request.form["phone"])
    r.save()
    return jsonify({"message":"Registration successful"})

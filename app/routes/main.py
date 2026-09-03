from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from datetime import datetime
from app.models import Donation, Volunteer, Event, Contact, Setting
import secrets

main_bp = Blueprint("main", __name__)

@main_bp.route("/")
def home():
    events = []
    slider_items = []
    packages = []
    stats = {}
    general = {}

    try:
        all_events = Event.get_all(active_only=True)
        if all_events:
            events = all_events[:3]

        slider_items = Setting.get("hero_slider", [])
        if not slider_items:
            slider_items = [
                {"type": "image", "url": "https://images.unsplash.com/photo-1488521787991-ed7bbaae773c?q=80&w=2070"},
                {"type": "image", "url": "https://images.unsplash.com/photo-1509059852496-f3822ae057bf?q=80&w=2080"}
            ]

        # Fetch causes from DB instead of static setting
        from app.models import Cause
        packages = Cause.get_all(active_only=True)

        # Fallback if no causes in DB
        if not packages:
            packages = [
                {"title": "Feed a Homeless", "amount": "60", "short_description": "Provide one nutritious meal to a homeless person.", "tag": "Hot Meals", "image_url": "https://images.unsplash.com/photo-1593113598332-cd288d649433?auto=format&fit=crop&w=400&q=80", "slug": "feed-a-homeless"},
                {"title": "Plant a Tree", "amount": "70", "short_description": "Help restore nature by planting a native tree.", "tag": "Eco Action", "image_url": "https://images.unsplash.com/photo-1542601906990-b4d3fb778b09?auto=format&fit=crop&w=400&q=80", "slug": "plant-a-tree"}
            ]

        stats = Setting.get("impact_stats", {
            "lives_impacted": "50,000+",
            "volunteers_count": "1,200+",
            "total_donations": "₹10 Cr+"
        })

        general = Setting.get("general_info", {
            "whatsapp": "+91 00000 00000",
            "instagram": "@navsahaay"
        })

        programmes = Setting.get("programmes", [
            {"title": "Education", "description": "Education and nutrition for children.", "icon_color": "#2563eb", "bg_color": "#eff6ff", "svg": '<svg fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253"></path></svg>'},
            {"title": "Healthcare", "description": "Healthcare services for communities.", "icon_color": "#9333ea", "bg_color": "#f5f3ff", "svg": '<svg fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z"></path></svg>'}
        ])

    except Exception as e:
        print(f"Error fetching home data: {e}")

    return render_template("home.html",
        events=events,
        slider_items=slider_items,
        packages=packages,
        stats=stats,
        general=general,
        programmes=programmes)

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

@main_bp.route("/cause/<slug>")
def cause_detail(slug):
    from app.models import Cause
    cause = Cause.get_by_slug(slug)
    if not cause or not cause.active:
        return render_template("404.html"), 404

    return render_template("cause_detail.html", cause=cause)

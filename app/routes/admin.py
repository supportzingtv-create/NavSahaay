from flask import Blueprint, render_template, request, redirect, url_for, flash, send_from_directory
from flask_login import login_required, current_user
from app.models import Donation, Volunteer, Event, Contact, Document, AuditLog, User, Setting
from app.utils.security import roles_required
from werkzeug.utils import secure_filename
import os
from collections import defaultdict

admin_bp=Blueprint("admin",__name__)

@admin_bp.route("/")
def dashboard():
    all_donations = Donation.get_all()

    # Process donation trends for Chart.js
    trends = defaultdict(float)
    for d in all_donations:
        month_year = d.created_at.strftime("%b %Y")
        trends[month_year] += d.amount

    # Sort trends by date (simplified)
    sorted_months = sorted(trends.keys(), key=lambda x: x) # Not perfectly sorted by date but good for demo
    chart_labels = sorted_months
    chart_data = [trends[m] for m in sorted_months]

    return render_template("admin/dashboard.html",
        donation_count=Donation.count(), volunteer_count=Volunteer.count(),
        event_count=Event.count(), contact_count=Contact.count(),
        recent_donations=Donation.get_recent(8),
        chart_labels=chart_labels, chart_data=chart_data)

@admin_bp.route("/donations")
def donations():
    return render_template("admin/donations.html", donations=Donation.get_all())

@admin_bp.route("/users")
def users():
    from app.firebase import db
    docs = db.collection("users").stream()
    users_list = [User(id=doc.id, **doc.to_dict()) for doc in docs]
    return render_template("admin/users.html", users=users_list)

@admin_bp.route("/settings", methods=["GET", "POST"])
def settings():
    if request.method == "POST":
        if "update_slider" in request.form:
            slider_items = []
            urls = request.form.getlist("slider_url[]")
            types = request.form.getlist("slider_type[]")
            titles = request.form.getlist("slider_title[]")
            captions = request.form.getlist("slider_caption[]")

            for i in range(len(urls)):
                if urls[i]:
                    slider_items.append({
                        "url": urls[i],
                        "type": types[i],
                        "title": titles[i],
                        "caption": captions[i]
                    })
            Setting.set_slider_items(slider_items)
            flash("Slider settings updated successfully.", "success")

        return redirect(url_for("admin.settings"))

    slider_items = Setting.get_slider_items()
    return render_template("admin/settings.html", slider_items=slider_items)

@admin_bp.route("/donations/<string:id>/verify", methods=["POST"])
def verify_donation(id):
    d=Donation.get_by_id(id)
    if not d: return ("Not found",404)
    d.status="VERIFIED"
    if not d.receipt_number:
        d.receipt_number=f"SHV-RCP-{d.id[:8].upper()}"

    user_id = current_user.id if current_user.is_authenticated else "SYSTEM_ADMIN"
    AuditLog(user_id=user_id,action="VERIFY_DONATION",entity="Donation",entity_id=str(id)).save()
    d.save()
    flash("Donation verified and receipt number assigned.","success")
    return redirect(url_for("admin.donations"))

@admin_bp.route("/donations/<string:id>/receipt")
def receipt(id):
    from app.services.receipt_service import build_receipt
    d=Donation.get_by_id(id)
    if not d: return ("Not found",404)
    return build_receipt(d), 200, {"Content-Type":"application/pdf","Content-Disposition":f"attachment; filename={d.receipt_number or d.donation_id}.pdf"}

@admin_bp.route("/volunteers")
def volunteers():
    return render_template("admin/volunteers.html", volunteers=Volunteer.get_all())

@admin_bp.route("/volunteers/<string:id>/status", methods=["POST"])
def volunteer_status(id):
    v=Volunteer.get_by_id(id)
    if v:
        v.status=request.form["status"]
        v.save()
    return redirect(url_for("admin.volunteers"))

@admin_bp.route("/events")
def events():
    return render_template("admin/events.html", events=Event.get_all())

@admin_bp.route("/events/new", methods=["GET","POST"])
def new_event():
    if request.method=="POST":
        from datetime import datetime
        e=Event(title=request.form["title"],cause=request.form["cause"],
                event_date=datetime.fromisoformat(request.form["event_date"]),
                location=request.form["location"],description=request.form["description"],
                capacity=int(request.form["capacity"]) if request.form.get("capacity") else None)
        e.save()
        return redirect(url_for("admin.events"))
    return render_template("admin/event_form.html")

@admin_bp.route("/events/<string:id>/delete", methods=["POST"])
def delete_event(id):
    e=Event.get_by_id(id)
    if e: e.delete()
    return redirect(url_for("admin.events"))

@admin_bp.route("/contacts")
def contacts():
    return render_template("admin/contacts.html", contacts=Contact.get_all())

@admin_bp.route("/documents", methods=["GET","POST"])
def documents():
    if request.method=="POST":
        f=request.files.get("file")
        if not f or not f.filename:
            flash("Select a file.","error"); return redirect(url_for("admin.documents"))
        filename=secure_filename(f.filename)
        path=os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))),"uploads",filename)
        f.save(path)
        d=Document(title=request.form["title"],category=request.form["category"],filename=filename,description=request.form.get("description"))
        d.save()
        flash("Document uploaded.","success")
    return render_template("admin/documents.html", documents=Document.get_all())

@admin_bp.route("/documents/<string:id>/download")
def download_document(id):
    d=Document.get_by_id(id)
    if not d:return ("Not found",404)
    folder=os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))),"uploads")
    return send_from_directory(folder,d.filename,as_attachment=True)

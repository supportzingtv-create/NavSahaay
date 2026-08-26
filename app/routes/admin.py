from flask import Blueprint, render_template, request, redirect, url_for, flash, send_from_directory
from flask_login import login_required, current_user
from app import db
from app.models import Donation, Volunteer, Event, Contact, Document, AuditLog
from app.utils.security import roles_required
from werkzeug.utils import secure_filename
import os

admin_bp=Blueprint("admin",__name__)

@admin_bp.route("/")
@login_required
def dashboard():
    return render_template("admin/dashboard.html",
        donation_count=Donation.query.count(), volunteer_count=Volunteer.query.count(),
        event_count=Event.query.count(), contact_count=Contact.query.count(),
        recent_donations=Donation.query.order_by(Donation.created_at.desc()).limit(8).all())

@admin_bp.route("/donations")
@login_required
def donations():
    return render_template("admin/donations.html", donations=Donation.query.order_by(Donation.created_at.desc()).all())

@admin_bp.route("/donations/<int:id>/verify", methods=["POST"])
@login_required
@roles_required("SUPER_ADMIN","FINANCE")
def verify_donation(id):
    d=db.session.get(Donation,id)
    if not d: return ("Not found",404)
    d.status="VERIFIED"
    if not d.receipt_number:
        d.receipt_number=f"SHV-RCP-{d.id:06d}"
    db.session.add(AuditLog(user_id=current_user.id,action="VERIFY_DONATION",entity="Donation",entity_id=str(id)))
    db.session.commit()
    flash("Donation verified and receipt number assigned.","success")
    return redirect(url_for("admin.donations"))

@admin_bp.route("/donations/<int:id>/receipt")
@login_required
def receipt(id):
    from app.services.receipt_service import build_receipt
    d=db.session.get(Donation,id)
    if not d: return ("Not found",404)
    return build_receipt(d), 200, {"Content-Type":"application/pdf","Content-Disposition":f"attachment; filename={d.receipt_number or d.donation_id}.pdf"}

@admin_bp.route("/volunteers")
@login_required
def volunteers():
    return render_template("admin/volunteers.html", volunteers=Volunteer.query.order_by(Volunteer.created_at.desc()).all())

@admin_bp.route("/volunteers/<int:id>/status", methods=["POST"])
@login_required
@roles_required("SUPER_ADMIN","EDITOR")
def volunteer_status(id):
    v=db.session.get(Volunteer,id)
    v.status=request.form["status"]; db.session.commit()
    return redirect(url_for("admin.volunteers"))

@admin_bp.route("/events")
@login_required
def events():
    return render_template("admin/events.html", events=Event.query.order_by(Event.event_date.asc()).all())

@admin_bp.route("/events/new", methods=["GET","POST"])
@login_required
@roles_required("SUPER_ADMIN","EDITOR")
def new_event():
    if request.method=="POST":
        from datetime import datetime
        e=Event(title=request.form["title"],cause=request.form["cause"],
                event_date=datetime.fromisoformat(request.form["event_date"]),
                location=request.form["location"],description=request.form["description"],
                capacity=int(request.form["capacity"]) if request.form.get("capacity") else None)
        db.session.add(e); db.session.commit()
        return redirect(url_for("admin.events"))
    return render_template("admin/event_form.html")

@admin_bp.route("/events/<int:id>/delete", methods=["POST"])
@login_required
@roles_required("SUPER_ADMIN")
def delete_event(id):
    e=db.session.get(Event,id)
    if e: db.session.delete(e); db.session.commit()
    return redirect(url_for("admin.events"))

@admin_bp.route("/contacts")
@login_required
def contacts():
    return render_template("admin/contacts.html", contacts=Contact.query.order_by(Contact.created_at.desc()).all())

@admin_bp.route("/documents", methods=["GET","POST"])
@login_required
@roles_required("SUPER_ADMIN","EDITOR")
def documents():
    if request.method=="POST":
        f=request.files.get("file")
        if not f or not f.filename:
            flash("Select a file.","error"); return redirect(url_for("admin.documents"))
        filename=secure_filename(f.filename)
        path=os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))),"uploads",filename)
        f.save(path)
        d=Document(title=request.form["title"],category=request.form["category"],filename=filename,description=request.form.get("description"))
        db.session.add(d); db.session.commit()
        flash("Document uploaded.","success")
    return render_template("admin/documents.html", documents=Document.query.order_by(Document.uploaded_at.desc()).all())

@admin_bp.route("/documents/<int:id>/download")
def download_document(id):
    d=db.session.get(Document,id)
    if not d:return ("Not found",404)
    folder=os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))),"uploads")
    return send_from_directory(folder,d.filename,as_attachment=True)

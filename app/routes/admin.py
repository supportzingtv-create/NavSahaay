from flask import Blueprint, render_template, request, redirect, url_for, flash, send_from_directory
from flask_login import login_required, current_user
from app.models import Donation, Volunteer, Event, Contact, Document, AuditLog, User, Setting
from app.utils.security import roles_required
from werkzeug.utils import secure_filename
import os
from collections import defaultdict

admin_bp=Blueprint("admin",__name__)

@admin_bp.route("/dashboard")
@login_required
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
@login_required
def donations():
    return render_template("admin/donations.html", donations=Donation.get_all())

@admin_bp.route("/users")
@login_required
@roles_required("SUPER_ADMIN")
def users():
    from app.firebase import db
    docs = db.collection("users").stream()
    users_list = [User(id=doc.id, **doc.to_dict()) for doc in docs]
    return render_template("admin/users.html", users=users_list)

@admin_bp.route("/settings", methods=["GET", "POST"])
@login_required
@roles_required("SUPER_ADMIN", "EDITOR")
def settings():
    if request.method == "POST":
        action = request.form.get("action")

        if action == "update_slider":
            items = []
            urls = request.form.getlist("url[]")
            types = request.form.getlist("type[]")
            for i in range(len(urls)):
                if urls[i]: items.append({"url": urls[i], "type": types[i]})
            Setting.set("hero_slider", items)
            flash("Slider updated.", "success")

        elif action == "update_stats":
            stats = {
                "lives_impacted": request.form.get("lives_impacted"),
                "volunteers_count": request.form.get("volunteers_count"),
                "total_donations": request.form.get("total_donations")
            }
            Setting.set("impact_stats", stats)
            flash("Impact stats updated.", "success")

        elif action == "update_packages":
            pkgs = []
            titles = request.form.getlist("title[]")
            amounts = request.form.getlist("amount[]")
            descs = request.form.getlist("description[]")
            imgs = request.form.getlist("img[]")
            tags = request.form.getlist("tag[]")
            for i in range(len(titles)):
                if titles[i]:
                    pkgs.append({
                        "title": titles[i], "amount": amounts[i],
                        "description": descs[i], "img": imgs[i], "tag": tags[i]
                    })
            Setting.set("donation_packages", pkgs)
            flash("Packages updated.", "success")

        elif action == "update_general":
            general = {
                "whatsapp": request.form.get("whatsapp"),
                "instagram": request.form.get("instagram")
            }
            Setting.set("general_info", general)
            flash("General info updated.", "success")

        elif action == "update_programmes":
            progs = []
            titles = request.form.getlist("title[]")
            descs = request.form.getlist("description[]")
            i_colors = request.form.getlist("icon_color[]")
            b_colors = request.form.getlist("bg_color[]")
            svgs = request.form.getlist("svg[]")
            for i in range(len(titles)):
                if titles[i]:
                    progs.append({
                        "title": titles[i], "description": descs[i],
                        "icon_color": i_colors[i], "bg_color": b_colors[i], "svg": svgs[i]
                    })
            Setting.set("programmes", progs)
            flash("Programmes updated.", "success")

        elif action == "update_testimonials":
            items = []
            names = request.form.getlist("name[]")
            roles = request.form.getlist("role[]")
            quotes = request.form.getlist("quote[]")
            imgs = request.form.getlist("img[]")
            for i in range(len(names)):
                if names[i]:
                    items.append({"name": names[i], "role": roles[i], "quote": quotes[i], "img": imgs[i]})
            Setting.set("testimonials", items)
            flash("Testimonials updated.", "success")

        elif action == "update_partners":
            items = []
            names = request.form.getlist("partner_name[]")
            logos = request.form.getlist("logo[]")
            for i in range(len(names)):
                if names[i]:
                    items.append({"name": names[i], "logo": logos[i]})
            Setting.set("partners", items)
            flash("Partners updated.", "success")

        elif action == "update_faqs":
            items = []
            ques = request.form.getlist("question[]")
            ans = request.form.getlist("answer[]")
            for i in range(len(ques)):
                if ques[i]:
                    items.append({"question": ques[i], "answer": ans[i]})
            Setting.set("faqs", items)
            flash("FAQs updated.", "success")

        elif action == "update_seo":
            seo = {
                "title": request.form.get("seo_title"),
                "description": request.form.get("seo_description"),
                "keywords": request.form.get("seo_keywords"),
                "og_image": request.form.get("og_image")
            }
            Setting.set("seo_meta", seo)

            social = {
                "whatsapp": request.form.get("whatsapp"),
                "instagram": request.form.get("instagram"),
                "facebook": request.form.get("facebook"),
                "twitter": request.form.get("twitter"),
                "youtube": request.form.get("youtube"),
                "email": request.form.get("contact_email")
            }
            Setting.set("social_links", social)
            flash("SEO and Social settings updated.", "success")

        return redirect(url_for("admin.settings"))

    return render_template("admin/settings.html",
        slider_items=Setting.get("hero_slider", []),
        stats=Setting.get("impact_stats", {}),
        packages=Setting.get("donation_packages", []),
        general=Setting.get("general_info", {}),
        programmes=Setting.get("programmes", []),
        testimonials=Setting.get("testimonials", []),
        partners=Setting.get("partners", []),
        faqs=Setting.get("faqs", []),
        seo=Setting.get("seo_meta", {}),
        social=Setting.get("social_links", {}))

@admin_bp.route("/donations/<string:id>/verify", methods=["POST"])
@login_required
@roles_required("SUPER_ADMIN","FINANCE")
def verify_donation(id):
    d=Donation.get_by_id(id)
    if not d: return ("Not found",404)
    d.status="VERIFIED"
    if not d.receipt_number:
        d.receipt_number=f"SHV-RCP-{d.id[:8].upper()}"

    AuditLog(user_id=current_user.id,action="VERIFY_DONATION",entity="Donation",entity_id=str(id)).save()
    d.save()
    flash("Donation verified and receipt number assigned.","success")
    return redirect(url_for("admin.donations"))

@admin_bp.route("/donations/<string:id>/receipt")
@login_required
def receipt(id):
    from app.services.receipt_service import build_receipt
    d=Donation.get_by_id(id)
    if not d: return ("Not found",404)
    return build_receipt(d), 200, {"Content-Type":"application/pdf","Content-Disposition":f"attachment; filename={d.receipt_number or d.donation_id}.pdf"}

@admin_bp.route("/volunteers")
@login_required
def volunteers():
    return render_template("admin/volunteers.html", volunteers=Volunteer.get_all())

@admin_bp.route("/volunteers/<string:id>/status", methods=["POST"])
@login_required
@roles_required("SUPER_ADMIN","EDITOR")
def volunteer_status(id):
    v=Volunteer.get_by_id(id)
    if v:
        v.status=request.form["status"]
        v.save()
    return redirect(url_for("admin.volunteers"))

@admin_bp.route("/events")
@login_required
def events():
    return render_template("admin/events.html", events=Event.get_all())

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
        e.save()
        return redirect(url_for("admin.events"))
    return render_template("admin/event_form.html")

@admin_bp.route("/events/<string:id>/delete", methods=["POST"])
@login_required
@roles_required("SUPER_ADMIN")
def delete_event(id):
    e=Event.get_by_id(id)
    if e: e.delete()
    return redirect(url_for("admin.events"))

@admin_bp.route("/contacts")
@login_required
def contacts():
    return render_template("admin/contacts.html", contacts=Contact.get_all())

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
        d.save()
        flash("Document uploaded.","success")
    return render_template("admin/documents.html", documents=Document.get_all())

@admin_bp.route("/documents/<string:id>/download")
@login_required
def download_document(id):
    d=Document.get_by_id(id)
    if not d:return ("Not found",404)
    folder=os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))),"uploads")
    return send_from_directory(folder,d.filename,as_attachment=True)

@admin_bp.route("/causes")
@login_required
def causes():
    from app.models import Cause
    return render_template("admin/causes.html", causes=Cause.get_all())

@admin_bp.route("/causes/new", methods=["GET", "POST"])
@login_required
@roles_required("SUPER_ADMIN", "EDITOR")
def new_cause():
    from app.models import Cause
    if request.method == "POST":
        c = Cause(
            title=request.form["title"],
            slug=request.form.get("slug"),
            tag=request.form["tag"],
            amount=float(request.form["amount"]),
            short_description=request.form["short_description"],
            description=request.form["description"],
            content=request.form["content"],
            image_url=request.form["image_url"],
            active=bool(request.form.get("active"))
        )
        c.save()
        flash("New donation cause created successfully.", "success")
        return redirect(url_for("admin.causes"))
    return render_template("admin/cause_form.html", cause=None)

@admin_bp.route("/causes/<string:id>/edit", methods=["GET", "POST"])
@login_required
@roles_required("SUPER_ADMIN", "EDITOR")
def edit_cause(id):
    from app.models import Cause
    c = Cause.get_by_id(id)
    if not c:
        flash("Cause not found.", "error")
        return redirect(url_for("admin.causes"))

    if request.method == "POST":
        c.title = request.form["title"]
        c.slug = request.form.get("slug")
        c.tag = request.form["tag"]
        c.amount = float(request.form["amount"])
        c.short_description = request.form["short_description"]
        c.description = request.form["description"]
        c.content = request.form["content"]
        c.image_url = request.form["image_url"]
        c.active = bool(request.form.get("active"))
        c.save()
        flash("Cause updated successfully.", "success")
        return redirect(url_for("admin.causes"))

    return render_template("admin/cause_form.html", cause=c)

@admin_bp.route("/causes/<string:id>/delete", methods=["POST"])
@login_required
@roles_required("SUPER_ADMIN")
def delete_cause(id):
    from app.models import Cause
    c = Cause.get_by_id(id)
    if c:
        c.delete()
        flash("Cause deleted.", "success")
    return redirect(url_for("admin.causes"))


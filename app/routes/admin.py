from flask import Blueprint, render_template, request, redirect, url_for, flash, send_from_directory, jsonify
from flask_login import login_required, current_user
from app.models import Donation, Volunteer, Event, Contact, Document, AuditLog, User, Setting
from app.utils.security import roles_required
from werkzeug.utils import secure_filename
from app.services.r2_service import r2_service
import os
from collections import defaultdict

admin_bp=Blueprint("admin",__name__)
HERO_SLIDER_R2_KEY = "settings/hero_slider.json"

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
            titles = request.form.getlist("title[]")
            subtitles = request.form.getlist("subtitle[]")
            positions = request.form.getlist("position[]")
            opacities = request.form.getlist("opacity[]")
            fits = request.form.getlist("fit[]")
            img_positions = request.form.getlist("img_position[]")
            btn_texts = request.form.getlist("btn_text[]")
            btn_links = request.form.getlist("btn_link[]")
            btn_colors = request.form.getlist("btn_color[]")
            for i in range(len(urls)):
                if urls[i]:
                    items.append({
                        "url": urls[i],
                        "type": types[i] if i < len(types) else "image",
                        "title": titles[i] if i < len(titles) else "",
                        "subtitle": subtitles[i] if i < len(subtitles) else "",
                        "position": positions[i] if i < len(positions) else "bottom-left",
                        "opacity": opacities[i] if i < len(opacities) else "100",
                        "fit": fits[i] if i < len(fits) else "cover",
                        "img_position": img_positions[i] if i < len(img_positions) else "center",
                        "btn_text": btn_texts[i] if i < len(btn_texts) else "Donate Now",
                        "btn_link": btn_links[i] if i < len(btn_links) else "/causes",
                        "btn_color": btn_colors[i] if i < len(btn_colors) else "red"
                    })
            firebase_saved = Setting.set("hero_slider", items)
            r2_saved = False
            try:
                # Use the module-level HERO_SLIDER_R2_KEY directly
                r2_saved = r2_service.save_json(HERO_SLIDER_R2_KEY, items)
            except Exception as e:
                print(f"Hero slider R2 settings save failed: {e}")

            if firebase_saved or r2_saved:
                flash(f"Slider updated. {len(items)} slide(s) active.", "success")
            else:
                flash(
                    "Slider was not saved. Connect Firebase or Cloudflare R2 in deployment settings.",
                    "error"
                )

        elif action == "update_stats":
            stats = {
                "lives_impacted_mode": request.form.get("lives_impacted_mode", "manual"),
                "lives_impacted": request.form.get("lives_impacted"),
                "lives_impacted_base": request.form.get("lives_impacted_base", "0"),

                "volunteers_mode": request.form.get("volunteers_mode", "manual"),
                "volunteers_count": request.form.get("volunteers_count"),
                "volunteers_base": request.form.get("volunteers_base", "0"),

                "donations_mode": request.form.get("donations_mode", "manual"),
                "total_donations": request.form.get("total_donations"),
                "donations_base": request.form.get("donations_base", "0")
            }
            Setting.set("impact_stats", stats)
            flash("Impact stats configuration updated successfully.", "success")

        elif action == "update_packages":
            pkgs = []
            titles = request.form.getlist("title[]")
            amounts = request.form.getlist("amount[]")
            target_amounts = request.form.getlist("target_amount[]")
            raised_amounts = request.form.getlist("raised_amount[]")
            descs = request.form.getlist("description[]")
            imgs = request.form.getlist("img[]")
            tags = request.form.getlist("tag[]")
            fits = request.form.getlist("fit[]")
            img_positions = request.form.getlist("img_position[]")
            show_goals = request.form.getlist("show_goal[]")
            for i in range(len(titles)):
                if titles[i]:
                    try:
                        target_val = float(target_amounts[i]) if i < len(target_amounts) and target_amounts[i] else 100000
                    except (ValueError, TypeError):
                        target_val = 100000
                    try:
                        raised_val = float(raised_amounts[i]) if i < len(raised_amounts) and raised_amounts[i] else 0
                    except (ValueError, TypeError):
                        raised_val = 0
                    pkgs.append({
                        "title": titles[i],
                        "amount": amounts[i] if i < len(amounts) else "60",
                        "target_amount": target_val,
                        "raised_amount": raised_val,
                        "description": descs[i] if i < len(descs) else "",
                        "short_description": descs[i] if i < len(descs) else "",
                        "img": imgs[i] if i < len(imgs) else "",
                        "image_url": imgs[i] if i < len(imgs) else "",
                        "tag": tags[i] if i < len(tags) else "Cause",
                        "fit": fits[i] if i < len(fits) else "cover",
                        "img_position": img_positions[i] if i < len(img_positions) else "center",
                        "show_goal": show_goals[i] if i < len(show_goals) else "no",
                        "slug": titles[i].lower().replace(" ", "-")
                    })
            Setting.set("donation_packages", pkgs)
            try:
                r2_service.save_json("settings/donation_packages.json", pkgs)
            except Exception as e:
                print(f"R2 donation packages save error: {e}")
            flash("Causes cards updated successfully.", "success")

        elif action == "update_general":
            general = {
                "phone_number": request.form.get("phone_number"),
                "phone": request.form.get("phone_number"),
                "whatsapp": request.form.get("whatsapp"),
                "email": request.form.get("email"),
                "instagram": request.form.get("instagram")
            }
            Setting.set("general_info", general)
            try:
                r2_service.save_json("settings/general_info.json", general)
            except Exception as e:
                print(f"R2 general info save error: {e}")
            flash("Phone number and contact info updated successfully.", "success")

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

        elif action == "update_urgent_appeal":
            appeal = {
                "active": bool(request.form.get("urgent_active")),
                "text": request.form.get("urgent_text"),
                "link": request.form.get("urgent_link"),
                "btn_text": request.form.get("urgent_btn_text")
            }
            Setting.set("urgent_appeal", appeal)
            flash("Urgent Appeal updated.", "success")

        elif action == "update_matching":
            matching = {
                "active": bool(request.form.get("matching_active")),
                "multiplier": request.form.get("matching_multiplier", "2"),
                "text": request.form.get("matching_text")
            }
            Setting.set("donation_matching", matching)
            flash("Donation Matching updated.", "success")

        elif action == "update_transparency":
            ratios = {
                "programmes": request.form.get("ratio_programmes", "92"),
                "admin": request.form.get("ratio_admin", "5"),
                "fundraising": request.form.get("ratio_fundraising", "3")
            }
            Setting.set("transparency_ratios", ratios)
            flash("Transparency ratios updated.", "success")

        elif action == "update_gallery":
            import json
            gallery = []
            titles = request.form.getlist("title[]")
            captions = request.form.getlist("caption[]")
            categories = request.form.getlist("category[]")
            images_jsons = request.form.getlist("images_json[]")
            urls_fallback = request.form.getlist("url[]")
            fits = request.form.getlist("fit[]")
            img_positions = request.form.getlist("img_position[]")

            max_items = max(len(titles), len(captions), len(images_jsons), len(urls_fallback))
            for i in range(max_items):
                title = titles[i] if i < len(titles) else ""
                caption = captions[i] if i < len(captions) else ""
                category = categories[i] if i < len(categories) else "General"
                fit = fits[i] if i < len(fits) else "cover"
                img_pos = img_positions[i] if i < len(img_positions) else "center"

                imgs = []
                if i < len(images_jsons) and images_jsons[i]:
                    try:
                        parsed = json.loads(images_jsons[i])
                        if isinstance(parsed, list):
                            imgs = [u.strip() for u in parsed if u and u.strip()]
                    except Exception:
                        pass

                if not imgs and i < len(urls_fallback) and urls_fallback[i]:
                    imgs = [urls_fallback[i].strip()]

                if imgs or title or caption:
                    cover = imgs[0] if imgs else ""
                    gallery.append({
                        "title": title or "NavSahaay Initiative",
                        "caption": caption,
                        "category": category,
                        "images": imgs,
                        "url": cover,
                        "fit": fit,
                        "img_position": img_pos
                    })

            Setting.set("gallery_items", gallery)
            try:
                r2_service.save_json("settings/gallery_items.json", gallery)
            except Exception as e:
                print(f"R2 gallery save error: {e}")
            flash(f"Gallery updated successfully. {len(gallery)} album group(s) active.", "success")

        return redirect(url_for("admin.settings"))

    from app.firebase import db as settings_db
    slider_items = Setting.get("hero_slider", []) or []
    if not slider_items:
        slider_items = r2_service.get_json(HERO_SLIDER_R2_KEY, []) or []

    packages = Setting.get("donation_packages", []) or []
    if not packages:
        packages = r2_service.get_json("settings/donation_packages.json", []) or []

    general = Setting.get("general_info", {}) or {}
    if not general:
        general = r2_service.get_json("settings/general_info.json", {}) or {}

    gallery_items = Setting.get("gallery_items", []) or []
    if not gallery_items:
        gallery_items = r2_service.get_json("settings/gallery_items.json", []) or []

    return render_template("admin/settings.html",
        slider_items=slider_items,
        settings_db_connected=settings_db is not None,
        stats=Setting.get("impact_stats", {}),
        packages=packages,
        general=general,
        gallery_items=gallery_items,
        programmes=Setting.get("programmes", []),
        testimonials=Setting.get("testimonials", []),
        partners=Setting.get("partners", []),
        faqs=Setting.get("faqs", []),
        seo=Setting.get("seo_meta", {}),
        social=Setting.get("social_links", {}),
        urgent=Setting.get("urgent_appeal", {}),
        matching=Setting.get("donation_matching", {}),
        transparency=Setting.get("transparency_ratios", {"programmes":"92", "admin":"5", "fundraising":"3"}))

@admin_bp.route("/upload-media", methods=["POST"])
@login_required
def upload_media():
    f = request.files.get("file")
    if not f: return jsonify({"error": "No file"}), 400

    try:
        url = r2_service.upload_file(f, folder="media")
        return jsonify({"url": url})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

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

        try:
            url = r2_service.upload_file(f, folder="documents")
            d=Document(title=request.form["title"], category=request.form["category"],
                       filename=url, description=request.form.get("description"))
            d.save()
            flash("Document uploaded to R2.","success")
        except Exception as e:
            flash(f"Upload failed: {str(e)}", "error")

    return render_template("admin/documents.html", documents=Document.get_all())

@admin_bp.route("/documents/<string:id>/download")
@login_required
def download_document(id):
    d=Document.get_by_id(id)
    if not d: return ("Not found", 404)
    if d.filename.startswith("http"):
        return redirect(d.filename)
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
            category=request.form["category"],
            amount=float(request.form["amount"]),
            target_amount=float(request.form.get("target_amount", 0)),
            raised_amount=float(request.form.get("raised_amount", 0)),
            short_description=request.form["short_description"],
            description=request.form["description"],
            content=request.form["content"],
            image_url=request.form["image_url"],
            gallery_images=request.form.getlist("gallery_images[]"),
            impact_unit_name=request.form.get("impact_unit_name"),
            impact_unit_cost=float(request.form.get("impact_unit_cost", 0)),
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
        c.category = request.form["category"]
        c.amount = float(request.form["amount"])
        c.target_amount = float(request.form.get("target_amount", 0))
        c.raised_amount = float(request.form.get("raised_amount", 0))
        c.short_description = request.form["short_description"]
        c.description = request.form["description"]
        c.content = request.form["content"]
        c.image_url = request.form["image_url"]
        c.gallery_images = request.form.getlist("gallery_images[]")
        c.impact_unit_name = request.form.get("impact_unit_name")
        c.impact_unit_cost = float(request.form.get("impact_unit_cost", 0))
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

@admin_bp.route("/impact-map", methods=["GET", "POST"])
@login_required
@roles_required("SUPER_ADMIN", "EDITOR")
def impact_map():
    from app.models import ImpactPin
    if request.method == "POST":
        p = ImpactPin(
            title=request.form["title"],
            description=request.form["description"],
            lat=request.form["lat"],
            lng=request.form["lng"],
            image_url=request.form["image_url"],
            active=bool(request.form.get("active"))
        )
        p.save()
        flash("Map pin added.", "success")
        return redirect(url_for("admin.impact_map"))
    return render_template("admin/impact_map.html", pins=ImpactPin.get_all())

@admin_bp.route("/impact-map/<string:id>/delete", methods=["POST"])
@login_required
@roles_required("SUPER_ADMIN")
def delete_pin(id):
    from app.models import ImpactPin
    p = ImpactPin.get_by_id(id)
    if p: p.delete()
    flash("Pin removed.", "success")
    return redirect(url_for("admin.impact_map"))

@admin_bp.route("/reports", methods=["GET", "POST"])
@login_required
@roles_required("SUPER_ADMIN", "EDITOR")
def reports():
    from app.models import Report
    if request.method == "POST":
        r = Report(
            title=request.form["title"],
            location=request.form["location"],
            image_url=request.form["image_url"],
            active=bool(request.form.get("active"))
        )
        r.save()
        flash("Ground report posted.", "success")
        return redirect(url_for("admin.reports"))
    return render_template("admin/reports.html", reports=Report.get_all())

@admin_bp.route("/reports/<string:id>/delete", methods=["POST"])
@login_required
@roles_required("SUPER_ADMIN")
def delete_report(id):
    from app.models import Report
    r = Report.get_by_id(id)
    if r: r.delete()
    flash("Report deleted.", "success")
    return redirect(url_for("admin.reports"))

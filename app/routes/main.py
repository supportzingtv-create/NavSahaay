from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, make_response
from datetime import datetime
from app.models import Donation, Volunteer, Event, Contact, Setting
from app.services.r2_service import r2_service
import secrets

main_bp = Blueprint("main", __name__)
HERO_SLIDER_R2_KEY = "settings/hero_slider.json"

@main_bp.route("/")
def home():
    # 1. Initialize all variables with empty/default values first (Safety Net)
    events = []
    slider_items = []
    packages = []
    stats = {
        "lives_impacted": "50,000+",
        "volunteers_count": "1,200+",
        "total_donations": "₹10 Cr+"
    }
    general = {
        "whatsapp": "+91 00000 00000",
        "instagram": "@navsahaay"
    }
    testimonials = []
    partners = []
    faqs = []
    seo = {
        "title": "NavSahaay Foundation | Leading NGO for Charity & Social Welfare",
        "description": "NavSahaay provides 100% transparency with photo/video proof for every donation.",
        "keywords": "NGO, Charity, India, Welfare, Donation"
    }
    social = general
    ground_reports = []
    leaderboard = []
    impact_pins = []
    programmes = [
        {"title": "Education", "description": "Quality education and nutrition for underprivileged children.", "icon_color": "#2563eb", "bg_color": "#eff6ff", "svg": '<svg fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253"></path></svg>'},
        {"title": "Healthcare", "description": "Mobile clinics and healthcare services for remote communities.", "icon_color": "#2563eb", "bg_color": "#eff6ff", "svg": '<svg fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z"></path></svg>'},
        {"title": "Environment", "description": "Reforestation and waste management for a greener planet.", "icon_color": "#2563eb", "bg_color": "#eff6ff", "svg": '<svg fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3.055 11H5a2 2 0 012 2v1a2 2 0 002 2 2 2 0 012 2v2.945M8 3.935V5.5A2.5 2.5 0 0010.5 8h.5a2 2 0 012 2 2 2 0 104 0 2 2 0 012-2h1.064M15 20.488V18a2 2 0 012-2h3.064M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>'},
        {"title": "Women Empowerment", "description": "Skill development and financial independence for women.", "icon_color": "#2563eb", "bg_color": "#eff6ff", "svg": '<svg fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z"></path></svg>'},
        {"title": "Hunger Relief", "description": "Providing nutritious meals to homeless and daily wagers.", "icon_color": "#2563eb", "bg_color": "#eff6ff", "svg": '<svg fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 3h2l.4 2M7 13h10l4-8H5.4M7 13L5.4 5M7 13l-2.293 2.293c-.63.63-.184 1.707.707 1.707H17m0 0a2 2 0 100 4 2 2 0 000-4zm-8 2a2 2 0 11-4 0 2 2 0 014 0z"></path></svg>'},
        {"title": "Disaster Relief", "description": "Immediate support and rehabilitation during natural calamities.", "icon_color": "#2563eb", "bg_color": "#eff6ff", "svg": '<svg fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"></path></svg>'}
    ]

    try:
        # 2. Try fetching dynamic data from DB
        all_events = Event.get_all(active_only=True)
        if all_events:
            events = all_events[:3]

        # Fetch hero media from database (Firebase primary, R2 fallback)
        slider_db = Setting.get("hero_slider")
        if not slider_db:
            slider_db = r2_service.get_json(HERO_SLIDER_R2_KEY, [])

        if slider_db and isinstance(slider_db, list):
            slider_items = [
                item for item in slider_db
                if isinstance(item, dict) and item.get("url")
            ]

        if not slider_items:
            # Only show demo images if both databases are empty or unreachable
            slider_items = [
                {"type": "image", "url": "https://images.unsplash.com/photo-1488521787991-ed7bbaae773c?q=80&w=2070", "fit": "cover", "img_position": "center"},
                {"type": "image", "url": "https://images.unsplash.com/photo-1509059852496-f3822ae057bf?q=80&w=2080", "fit": "cover", "img_position": "center"}
            ]

        packages_setting = Setting.get("donation_packages")
        if not packages_setting:
            packages_setting = r2_service.get_json("settings/donation_packages.json", [])

        packages = []
        if packages_setting and isinstance(packages_setting, list):
            for pkg in packages_setting:
                if isinstance(pkg, dict) and pkg.get("title"):
                    packages.append({
                        "title": pkg.get("title"),
                        "amount": pkg.get("amount", "60"),
                        "target_amount": pkg.get("target_amount") or 100000,
                        "raised_amount": pkg.get("raised_amount") or 0,
                        "short_description": pkg.get("description") or pkg.get("short_description") or "",
                        "tag": pkg.get("tag") or "Cause",
                        "image_url": pkg.get("img") or pkg.get("image_url") or "https://images.unsplash.com/photo-1593113598332-cd288d649433?auto=format&fit=crop&w=400&q=80",
                        "fit": pkg.get("fit") or "cover",
                        "img_position": pkg.get("img_position") or "center",
                        "show_goal": pkg.get("show_goal", "no"),
                        "slug": pkg.get("slug") or pkg.get("title", "").lower().replace(" ", "-")
                    })

        if not packages:
            from app.models import Cause
            causes_db = Cause.get_all(active_only=True)
            if causes_db:
                packages = causes_db

        if not packages:
            packages = [
                {"title": "Feed a Homeless", "amount": "60", "target_amount": 100000, "raised_amount": 35000, "short_description": "Provide one nutritious meal to a homeless person.", "tag": "Hot Meals", "image_url": "https://images.unsplash.com/photo-1593113598332-cd288d649433?auto=format&fit=crop&w=400&q=80", "slug": "feed-a-homeless"},
                {"title": "Plant a Tree", "amount": "70", "target_amount": 50000, "raised_amount": 18000, "short_description": "Help restore nature by planting a native tree.", "tag": "Eco Action", "image_url": "https://images.unsplash.com/photo-1542601906990-b4d3fb778b09?auto=format&fit=crop&w=400&q=80", "slug": "plant-a-tree"}
            ]

        stats_db = Setting.get("impact_stats")
        if stats_db:
            # 1. Lives Impacted calculation
            if stats_db.get("lives_impacted_mode") == "auto":
                try:
                    base_li = int(stats_db.get("lives_impacted_base") or 0)
                except (ValueError, TypeError):
                    base_li = 50000
                try:
                    all_dons_temp = Donation.get_all()
                    verified_dons_count = len([d for d in all_dons_temp if d.status == "VERIFIED"])
                except Exception:
                    verified_dons_count = 0
                lives_impacted_val = f"{base_li + (verified_dons_count * 5):,}+"
            else:
                lives_impacted_val = stats_db.get("lives_impacted") or "50,000+"

            # 2. Volunteers Count calculation
            if stats_db.get("volunteers_mode") == "auto":
                try:
                    base_v = int(stats_db.get("volunteers_base") or 0)
                except (ValueError, TypeError):
                    base_v = 1200
                try:
                    v_count = Volunteer.count()
                except Exception:
                    v_count = 0
                volunteers_val = f"{base_v + v_count:,}+"
            else:
                volunteers_val = stats_db.get("volunteers_count") or "1,200+"

            # 3. Total Donations calculation
            if stats_db.get("donations_mode") == "auto":
                try:
                    base_d = float(stats_db.get("donations_base") or 0)
                except (ValueError, TypeError):
                    base_d = 10000000
                try:
                    all_dons_temp = Donation.get_all()
                    db_total = sum(d.amount for d in all_dons_temp if d.status == "VERIFIED")
                except Exception:
                    db_total = 0
                total_amt = base_d + db_total
                if total_amt >= 10000000:
                    donations_val = f"₹{total_amt/10000000:.2f} Cr+"
                elif total_amt >= 100000:
                    donations_val = f"₹{total_amt/100000:.2f} Lakh+"
                else:
                    donations_val = f"₹{total_amt:,}+"
            else:
                donations_val = stats_db.get("total_donations") or "₹10 Cr+"

            stats = {
                "lives_impacted": lives_impacted_val,
                "volunteers_count": volunteers_val,
                "total_donations": donations_val,
                "lives_impacted_mode": stats_db.get("lives_impacted_mode", "manual"),
                "volunteers_mode": stats_db.get("volunteers_mode", "manual"),
                "donations_mode": stats_db.get("donations_mode", "manual"),
                "lives_impacted_base": stats_db.get("lives_impacted_base", "50000"),
                "volunteers_base": stats_db.get("volunteers_base", "1200"),
                "donations_base": stats_db.get("donations_base", "10000000")
            }

        general_db = Setting.get("general_info")
        if not general_db:
            general_db = r2_service.get_json("settings/general_info.json", {})
        if general_db: general = general_db

        testimonials = Setting.get("testimonials", [])
        partners = Setting.get("partners", [])
        faqs = Setting.get("faqs", [])

        seo_db = Setting.get("seo_meta")
        if seo_db: seo = seo_db

        social = Setting.get("social_links", general)

        from app.models import Report
        ground_reports = Report.get_all(active_only=True)[:10]

        # Monthly Leaderboard
        from datetime import datetime
        now = datetime.now()
        start_of_month = datetime(now.year, now.month, 1)

        all_donations = Donation.get_all()
        monthly_donors = {}
        for d in all_donations:
            if d.status == "VERIFIED" and d.created_at >= start_of_month:
                name = d.donor_name if not d.anonymous else "Anonymous Hero"
                monthly_donors[name] = monthly_donors.get(name, 0) + d.amount
        leaderboard = sorted(monthly_donors.items(), key=lambda x: x[1], reverse=True)[:5]

        from app.models import ImpactPin
        impact_pins = ImpactPin.get_all(active_only=True)

        prog_db = Setting.get("programmes")
        if prog_db: programmes = prog_db

    except Exception as e:
        print(f"CRITICAL: Error fetching home data from Firebase: {e}")
        # The variables already have default values, so the page will still render.

    response = make_response(render_template("home.html",
        events=events, slider_items=slider_items, packages=packages,
        stats=stats, general=general, programmes=programmes,
        testimonials=testimonials, partners=partners, faqs=faqs,
        seo=seo, social=social, ground_reports=ground_reports,
        leaderboard=leaderboard, impact_pins=impact_pins))
    # The hero is admin-managed; never let a cached homepage hide a newly
    # saved banner from the public site.
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    response.headers["Pragma"] = "no-cache"
    return response

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
        honor_name=request.form.get("honor_name"),
        honor_type=request.form.get("honor_type"),
        wish=request.form.get("wish"),
        sponsored_date=request.form.get("sponsored_date"),
        recipient_name=request.form.get("recipient_name"),
        recipient_email=request.form.get("recipient_email"),
        anonymous=bool(request.form.get("anonymous")), status="PENDING"
    )
    donation.save()
    return redirect(url_for("main.donation_success", id=donation.id))

@main_bp.route("/donation-success/<id>")
def donation_success(id):
    donation = Donation.get_by_id(id)
    if not donation:
        return redirect(url_for("main.home"))
    return render_template("donation_success.html", donation=donation)

@main_bp.route("/certificate/<id>")
def view_certificate(id):
    donation = Donation.get_by_id(id)
    if not donation or not donation.recipient_name:
        return redirect(url_for("main.home"))
    return render_template("certificate.html", donation=donation)

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

@main_bp.route("/gallery")
def gallery():
    gallery_items = Setting.get("gallery_items")
    if not gallery_items:
        gallery_items = r2_service.get_json("settings/gallery_items.json", []) or []

    if not gallery_items:
        gallery_items = [
            {
                "title": "Tree Plantation Drive 2026",
                "caption": "Planted 500+ saplings in Jaipur rural region with 50 local volunteers.",
                "category": "Environment",
                "images": [
                    "https://images.unsplash.com/photo-1542601906990-b4d3fb778b09?q=80&w=1200",
                    "https://images.unsplash.com/photo-1576085898323-218337e3e43c?q=80&w=1200",
                    "https://images.unsplash.com/photo-1513836279014-a89f7a76ae86?q=80&w=1200"
                ],
                "url": "https://images.unsplash.com/photo-1542601906990-b4d3fb778b09?q=80&w=1200"
            },
            {
                "title": "Warm Meal & Grocery Ration Drive",
                "caption": "Distributed hot nutritious meals and monthly ration kits to 200+ homeless families.",
                "category": "Food Drives",
                "images": [
                    "https://images.unsplash.com/photo-1488521787991-ed7bbaae773c?q=80&w=1200",
                    "https://images.unsplash.com/photo-1593113598332-cd288d649433?q=80&w=1200"
                ],
                "url": "https://images.unsplash.com/photo-1488521787991-ed7bbaae773c?q=80&w=1200"
            },
            {
                "title": "Digital Learning & School Kit Distribution",
                "caption": "Provided free textbooks, bags, uniforms and digital learning tools to children.",
                "category": "Education",
                "images": [
                    "https://images.unsplash.com/photo-1509059852496-f3822ae057bf?q=80&w=1200"
                ],
                "url": "https://images.unsplash.com/photo-1509059852496-f3822ae057bf?q=80&w=1200"
            },
            {
                "title": "Free Rural Health & Eye Camp",
                "caption": "Conducted free medical health checkups, eye tests, and medicine distribution.",
                "category": "Healthcare",
                "images": [
                    "https://images.unsplash.com/photo-1584515979956-d9f6e5d09982?q=80&w=1200"
                ],
                "url": "https://images.unsplash.com/photo-1584515979956-d9f6e5d09982?q=80&w=1200"
            },
            {
                "title": "Women Skill Development Workshop",
                "caption": "Organized self-reliance tailoring and handicraft training for underprivileged women.",
                "category": "Events",
                "images": [
                    "https://images.unsplash.com/photo-1573496359142-b8d87734a5a2?q=80&w=1200"
                ],
                "url": "https://images.unsplash.com/photo-1573496359142-b8d87734a5a2?q=80&w=1200"
            }
        ]

    # Normalize gallery items so each item has a list of 'images' and a 'url'
    for item in gallery_items:
        if "images" not in item or not isinstance(item["images"], list):
            item["images"] = [item.get("url")] if item.get("url") else []
        elif item["images"] and not item.get("url"):
            item["url"] = item["images"][0]

    categories = sorted(list(set(item.get("category", "General") for item in gallery_items if item.get("category"))))

    general = Setting.get("general_info") or r2_service.get_json("settings/general_info.json", {}) or {}
    social = Setting.get("social_links", general)

    response = make_response(render_template("gallery.html",
        gallery_items=gallery_items,
        categories=categories,
        general=general,
        social=social))
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    return response


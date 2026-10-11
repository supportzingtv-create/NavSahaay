from flask import Blueprint, jsonify
from app.models import Event, Donation, Volunteer

api_bp=Blueprint("api",__name__)

@api_bp.get("/events")
def events():
    return jsonify([{"id":e.id,"title":e.title,"cause":e.cause,"date":e.event_date.isoformat(),"location":e.location,"description":e.description} for e in Event.get_all(active_only=True)])

@api_bp.get("/stats")
def stats():
    all_donations = Donation.get_all()
    total_amount = sum(float(d.amount or 0) for d in all_donations)
    return jsonify({
        "donations": len(all_donations),
        "donation_amount": total_amount,
        "volunteers": Volunteer.count(),
        "events": Event.count()
    })

@api_bp.get("/recent-donations")
def recent_donations():
    try:
        dons = Donation.get_all()
        recent = dons[:30] if dons else []
        result = []
        for d in recent:
            name = "Supporter"
            if getattr(d, "anonymous", False):
                name = "A Generous Soul"
            elif getattr(d, "donor_name", None):
                name = d.donor_name.strip()

            try:
                amt = int(float(d.amount or 500))
            except Exception:
                amt = 500

            wish = getattr(d, "wish", None) or ""

            result.append({
                "name": name,
                "amount": amt,
                "cause": getattr(d, "cause", None) or "General Welfare",
                "wish": wish,
                "time": "Just now",
                "id": str(getattr(d, "id", "") or getattr(d, "donation_id", ""))
            })
        return jsonify({"status": "success", "donations": result})
    except Exception as e:
        return jsonify({"status": "error", "donations": []})

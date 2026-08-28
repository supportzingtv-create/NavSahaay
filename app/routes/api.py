from flask import Blueprint, jsonify
from app.models import Event, Donation, Volunteer

api_bp=Blueprint("api",__name__)

@api_bp.get("/events")
def events():
    return jsonify([{"id":e.id,"title":e.title,"cause":e.cause,"date":e.event_date.isoformat(),"location":e.location,"description":e.description} for e in Event.get_all(active_only=True)])

@api_bp.get("/stats")
def stats():
    all_donations = Donation.get_all()
    total_amount = sum(float(d.amount) for d in all_donations)
    return jsonify({
        "donations": len(all_donations),
        "donation_amount": total_amount,
        "volunteers": Volunteer.count(),
        "events": Event.count()
    })

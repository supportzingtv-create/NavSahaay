from flask import Blueprint, jsonify
from app.models import Event, Donation, Volunteer

api_bp=Blueprint("api",__name__)

@api_bp.get("/events")
def events():
    return jsonify([{"id":e.id,"title":e.title,"cause":e.cause,"date":e.event_date.isoformat(),"location":e.location,"description":e.description} for e in Event.query.filter_by(active=True).order_by(Event.event_date).all()])

@api_bp.get("/stats")
def stats():
    from sqlalchemy import func
    return jsonify({
        "donations": Donation.query.count(),
        "donation_amount": float(Donation.query.with_entities(func.coalesce(func.sum(Donation.amount),0)).scalar()),
        "volunteers": Volunteer.query.count(),
        "events": Event.query.filter_by(active=True).count()
    })

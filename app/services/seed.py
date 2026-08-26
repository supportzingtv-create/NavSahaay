import os
from datetime import datetime, timedelta
from app import db
from app.models import User, Event

def seed_admin_and_events():
    email = os.getenv("ADMIN_EMAIL", "admin@shivoham.local")
    password = os.getenv("ADMIN_PASSWORD", "Admin@123")
    if not User.query.filter_by(email=email).first():
        u = User(name="Shivoham Administrator", email=email, role="SUPER_ADMIN")
        u.set_password(password)
        db.session.add(u)
    if Event.query.count() == 0:
        now = datetime.now()
        events = [
            Event(title="Community Learning Drive", cause="Education", event_date=now+timedelta(days=18),
                  location="To be confirmed", description="Volunteer-led learning support session.", capacity=50),
            Event(title="Green Community Day", cause="Environment", event_date=now+timedelta(days=32),
                  location="To be confirmed", description="Environmental awareness and community activity.", capacity=100),
            Event(title="Community Health Camp", cause="Healthcare", event_date=now+timedelta(days=46),
                  location="To be confirmed", description="Health awareness and screening initiative.", capacity=100),
        ]
        db.session.add_all(events)
    db.session.commit()

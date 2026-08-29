import os
from datetime import datetime, timedelta
from app.models import User, Event

def seed_admin_and_events():
    email = os.getenv("ADMIN_EMAIL", "admin@navsahaay.org")
    password = os.getenv("ADMIN_PASSWORD", "Admin@123")

    user = User.get_by_email(email)
    if not user:
        user = User(id=None, name="NavSahaay Administrator", email=email, role="SUPER_ADMIN")
        user.set_password(password)
        user.save()
        print(f"Seeded new admin: {email}")
    else:
        # Update existing admin to ensure credentials match env vars
        user.set_password(password)
        user.role = "SUPER_ADMIN"
        user.save()
        print(f"Updated admin credentials: {email}")

    if Event.count() == 0:
        now = datetime.now()
        events = [
            Event(title="Community Learning Drive", cause="Education", event_date=now+timedelta(days=18),
                  location="To be confirmed", description="Volunteer-led learning support session.", capacity=50),
            Event(title="Green Community Day", cause="Environment", event_date=now+timedelta(days=32),
                  location="To be confirmed", description="Environmental awareness and community activity.", capacity=100),
            Event(title="Community Health Camp", cause="Healthcare", event_date=now+timedelta(days=46),
                  location="To be confirmed", description="Health awareness and screening initiative.", capacity=100),
        ]
        for e in events:
            e.save()
        print("Seeded initial events.")

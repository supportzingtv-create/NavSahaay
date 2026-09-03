import os
from datetime import datetime, timedelta
from app.models import User, Event

def seed_admin_and_events():
    try:
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

        from app.models import Cause
        if len(Cause.get_all()) == 0:
            causes = [
                Cause(title="Feed a Homeless", amount=60, tag="Hot Meals",
                      short_description="Provide one nutritious meal to a homeless person.",
                      description="Our feeding program ensures that no one goes to sleep hungry in our community.",
                      image_url="https://images.unsplash.com/photo-1593113598332-cd288d649433?auto=format&fit=crop&w=800&q=80",
                      content="<h3>Why Feed the Homeless?</h3><p>Hunger is a daily struggle for thousands. Your small contribution of ₹60 provides a fresh, nutritious hot meal...</p>"),
                Cause(title="Plant a Tree", amount=70, tag="Eco Action",
                      short_description="Help restore nature by planting a native tree.",
                      description="We are on a mission to plant 10,000 trees to combat climate change.",
                      image_url="https://images.unsplash.com/photo-1542601906990-b4d3fb778b09?auto=format&fit=crop&w=800&q=80",
                      content="<h3>Eco Action Mission</h3><p>Trees are the lungs of our planet. Join us in our reforestation efforts...</p>")
            ]
            for c in causes:
                c.save()
            print("Seeded initial donation causes.")
    except Exception as e:
        print(f"Seeding error: {e}")

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
                      impact_unit_name="Nutritious Meal", impact_unit_cost=60,
                      short_description="Provide one nutritious meal to a homeless person.",
                      description="Our feeding program ensures that no one goes to sleep hungry in our community.",
                      image_url="https://images.unsplash.com/photo-1593113598332-cd288d649433?auto=format&fit=crop&w=800&q=80",
                      content="<h3>Why Feed the Homeless?</h3><p>Hunger is a daily struggle for thousands. Your small contribution of ₹60 provides a fresh, nutritious hot meal...</p>"),
                Cause(title="Plant a Tree", amount=70, tag="Eco Action",
                      impact_unit_name="Native Tree", impact_unit_cost=70,
                      short_description="Help restore nature by planting a native tree.",
                      description="We are on a mission to plant 10,000 trees to combat climate change.",
                      image_url="https://images.unsplash.com/photo-1542601906990-b4d3fb778b09?auto=format&fit=crop&w=800&q=80",
                      content="<h3>Eco Action Mission</h3><p>Trees are the lungs of our planet. Join us in our reforestation efforts...</p>")
            ]
            for c in causes:
                c.save()
            print("Seeded initial donation causes.")

        from app.models import Setting
        existing_progs = Setting.get("programmes", [])
        if len(existing_progs) < 3:
            default_progs = [
                {"title": "Education", "description": "Quality education and nutrition for underprivileged children.", "icon_color": "#2563eb", "bg_color": "#eff6ff", "svg": '<svg fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253"></path></svg>'},
                {"title": "Healthcare", "description": "Mobile clinics and healthcare services for remote communities.", "icon_color": "#dc2626", "bg_color": "#fef2f2", "svg": '<svg fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z"></path></svg>'},
                {"title": "Environment", "description": "Reforestation and waste management for a greener planet.", "icon_color": "#059669", "bg_color": "#ecfdf5", "svg": '<svg fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3.055 11H5a2 2 0 012 2v1a2 2 0 002 2 2 2 0 012 2v2.945M8 3.935V5.5A2.5 2.5 0 0010.5 8h.5a2 2 0 012 2 2 2 0 104 0 2 2 0 012-2h1.064M15 20.488V18a2 2 0 012-2h3.064M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>'},
                {"title": "Women Empowerment", "description": "Skill development and financial independence for women.", "icon_color": "#d946ef", "bg_color": "#fdf4ff", "svg": '<svg fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z"></path></svg>'},
                {"title": "Hunger Relief", "description": "Providing nutritious meals to homeless and daily wagers.", "icon_color": "#f59e0b", "bg_color": "#fffbeb", "svg": '<svg fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 3h2l.4 2M7 13h10l4-8H5.4M7 13L5.4 5M7 13l-2.293 2.293c-.63.63-.184 1.707.707 1.707H17m0 0a2 2 0 100 4 2 2 0 000-4zm-8 2a2 2 0 11-4 0 2 2 0 014 0z"></path></svg>'},
                {"title": "Disaster Relief", "description": "Immediate support and rehabilitation during natural calamities.", "icon_color": "#4b5563", "bg_color": "#f3f4f6", "svg": '<svg fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"></path></svg>'}
            ]
            Setting.set("programmes", default_progs)
            print("Restored default programmes.")
    except Exception as e:
        print(f"Seeding error: {e}")

from app.firebase import db
from datetime import datetime

class Event:
    def __init__(self, id=None, title=None, cause=None, event_date=None,
                 location=None, description=None, capacity=None, active=True, created_at=None):
        self.id = id
        self.title = title
        self.cause = cause
        self.event_date = event_date
        self.location = location
        self.description = description
        self.capacity = capacity
        self.active = active
        self.created_at = created_at or datetime.now()

    def to_dict(self):
        return {
            "title": self.title,
            "cause": self.cause,
            "event_date": self.event_date,
            "location": self.location,
            "description": self.description,
            "capacity": self.capacity,
            "active": self.active,
            "created_at": self.created_at
        }

    @property
    def registrations(self):
        if not self.id: return []
        docs = db.collection("events").document(self.id).collection("registrations").stream()
        return [EventRegistration(id=doc.id, **doc.to_dict()) for doc in docs]

    @staticmethod
    def get_by_id(event_id):
        doc = db.collection("events").document(event_id).get()
        if doc.exists:
            return Event(id=doc.id, **doc.to_dict())
        return None

    @staticmethod
    def count():
        return len(db.collection("events").get())

    @staticmethod
    def get_all(active_only=False):
        query = db.collection("events")
        if active_only:
            query = query.where("active", "==", True)
        docs = query.order_by("event_date", direction="ASCENDING").stream()
        return [Event(id=doc.id, **doc.to_dict()) for doc in docs]

    def save(self):
        if self.id:
            db.collection("events").document(self.id).set(self.to_dict())
        else:
            _, doc_ref = db.collection("events").add(self.to_dict())
            self.id = doc_ref.id
        return self

    def delete(self):
        if self.id:
            db.collection("events").document(self.id).delete()

class EventRegistration:
    def __init__(self, id=None, event_id=None, name=None, email=None, phone=None, created_at=None):
        self.id = id
        self.event_id = event_id
        self.name = name
        self.email = email
        self.phone = phone
        self.created_at = created_at or datetime.now()

    def to_dict(self):
        return {
            "name": self.name,
            "email": self.email,
            "phone": self.phone,
            "created_at": self.created_at
        }

    def save(self):
        if not self.event_id: raise ValueError("event_id is required")
        if self.id:
            db.collection("events").document(self.event_id).collection("registrations").document(self.id).set(self.to_dict())
        else:
            _, doc_ref = db.collection("events").document(self.event_id).collection("registrations").add(self.to_dict())
            self.id = doc_ref.id
        return self

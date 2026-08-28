from datetime import datetime

class Volunteer:
    def __init__(self, id=None, reference_id=None, name=None, email=None, phone=None,
                 city=None, age=None, interest=None, availability=None, skills=None,
                 experience=None, source=None, status="NEW", created_at=None):
        self.id = id
        self.reference_id = reference_id
        self.name = name
        self.email = email
        self.phone = phone
        self.city = city
        self.age = age
        self.interest = interest
        self.availability = availability
        self.skills = skills
        self.experience = experience
        self.source = source
        self.status = status
        self.created_at = created_at or datetime.now()

    def to_dict(self):
        return {
            "reference_id": self.reference_id,
            "name": self.name,
            "email": self.email,
            "phone": self.phone,
            "city": self.city,
            "age": self.age,
            "interest": self.interest,
            "availability": self.availability,
            "skills": self.skills,
            "experience": self.experience,
            "source": self.source,
            "status": self.status,
            "created_at": self.created_at
        }

    @staticmethod
    def get_by_id(vol_id):
        from app.firebase import db
        if not vol_id or db is None: return None
        doc = db.collection("volunteers").document(vol_id).get()
        if doc.exists:
            return Volunteer(id=doc.id, **doc.to_dict())
        return None

    @staticmethod
    def count():
        from app.firebase import db
        if db is None: return 0
        return len(db.collection("volunteers").get())

    @staticmethod
    def get_all():
        from app.firebase import db
        if db is None: return []
        docs = db.collection("volunteers").order_by("created_at", direction="DESCENDING").stream()
        return [Volunteer(id=doc.id, **doc.to_dict()) for doc in docs]

    def save(self):
        from app.firebase import db
        if db is None: return None
        if self.id:
            db.collection("volunteers").document(self.id).set(self.to_dict())
        else:
            _, doc_ref = db.collection("volunteers").add(self.to_dict())
            self.id = doc_ref.id
        return self

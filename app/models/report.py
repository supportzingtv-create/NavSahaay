from datetime import datetime

class Report:
    def __init__(self, id=None, title=None, location=None, image_url=None, active=True, created_at=None):
        self.id = id
        self.title = title
        self.location = location
        self.image_url = image_url
        self.active = active
        self.created_at = created_at or datetime.now()

    def to_dict(self):
        return {
            "title": self.title,
            "location": self.location,
            "image_url": self.image_url,
            "active": self.active,
            "created_at": self.created_at
        }

    @staticmethod
    def get_all(active_only=False):
        from app.firebase import db
        if db is None: return []
        query = db.collection("reports")
        if active_only:
            query = query.where("active", "==", True)
        docs = query.order_by("created_at", direction="DESCENDING").stream()
        return [Report(id=doc.id, **doc.to_dict()) for doc in docs]

    @staticmethod
    def get_by_id(report_id):
        from app.firebase import db
        if not report_id or db is None: return None
        doc = db.collection("reports").document(report_id).get()
        if doc.exists:
            return Report(id=doc.id, **doc.to_dict())
        return None

    def save(self):
        from app.firebase import db
        if db is None: return None
        if self.id:
            db.collection("reports").document(self.id).set(self.to_dict())
        else:
            _, doc_ref = db.collection("reports").add(self.to_dict())
            self.id = doc_ref.id
        return self

    def delete(self):
        from app.firebase import db
        if self.id and db:
            db.collection("reports").document(self.id).delete()
            return True
        return False

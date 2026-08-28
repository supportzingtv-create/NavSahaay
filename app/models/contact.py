from datetime import datetime

class Contact:
    def __init__(self, id=None, name=None, email=None, subject=None, message=None, status="NEW", created_at=None):
        self.id = id
        self.name = name
        self.email = email
        self.subject = subject
        self.message = message
        self.status = status
        self.created_at = created_at or datetime.now()

    def to_dict(self):
        return {
            "name": self.name,
            "email": self.email,
            "subject": self.subject,
            "message": self.message,
            "status": self.status,
            "created_at": self.created_at
        }

    @staticmethod
    def count():
        from app.firebase import db
        if db is None: return 0
        return len(db.collection("contacts").get())

    @staticmethod
    def get_all():
        from app.firebase import db
        if db is None: return []
        docs = db.collection("contacts").order_by("created_at", direction="DESCENDING").stream()
        return [Contact(id=doc.id, **doc.to_dict()) for doc in docs]

    def save(self):
        from app.firebase import db
        if db is None: return None
        if self.id:
            db.collection("contacts").document(self.id).set(self.to_dict())
        else:
            _, doc_ref = db.collection("contacts").add(self.to_dict())
            self.id = doc_ref.id
        return self

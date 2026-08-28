from datetime import datetime

class Document:
    def __init__(self, id=None, title=None, category=None, filename=None, description=None, uploaded_at=None):
        self.id = id
        self.title = title
        self.category = category
        self.filename = filename
        self.description = description
        self.uploaded_at = uploaded_at or datetime.now()

    def to_dict(self):
        return {
            "title": self.title,
            "category": self.category,
            "filename": self.filename,
            "description": self.description,
            "uploaded_at": self.uploaded_at
        }

    @staticmethod
    def get_by_id(doc_id):
        from app.firebase import db
        if not doc_id or db is None: return None
        doc = db.collection("documents").document(doc_id).get()
        if doc.exists:
            return Document(id=doc.id, **doc.to_dict())
        return None

    @staticmethod
    def get_all():
        from app.firebase import db
        if db is None: return []
        docs = db.collection("documents").order_by("uploaded_at", direction="DESCENDING").stream()
        return [Document(id=doc.id, **doc.to_dict()) for doc in docs]

    def save(self):
        from app.firebase import db
        if db is None: return None
        if self.id:
            db.collection("documents").document(self.id).set(self.to_dict())
        else:
            _, doc_ref = db.collection("documents").add(self.to_dict())
            self.id = doc_ref.id
        return self

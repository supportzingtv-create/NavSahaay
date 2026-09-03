from datetime import datetime
import re

class Cause:
    def __init__(self, id=None, slug=None, title=None, description=None, short_description=None,
                 amount=0, image_url=None, tag=None, content=None, active=True, created_at=None):
        self.id = id
        self.slug = slug or self.generate_slug(title)
        self.title = title
        self.description = description
        self.short_description = short_description
        self.amount = amount
        self.image_url = image_url
        self.tag = tag
        self.content = content
        self.active = active
        self.created_at = created_at or datetime.now()

    @staticmethod
    def generate_slug(title):
        if not title: return ""
        return re.sub(r'[^a-z0-9]+', '-', title.lower()).strip('-')

    def to_dict(self):
        return {
            "slug": self.slug,
            "title": self.title,
            "description": self.description,
            "short_description": self.short_description,
            "amount": self.amount,
            "image_url": self.image_url,
            "tag": self.tag,
            "content": self.content,
            "active": self.active,
            "created_at": self.created_at
        }

    @staticmethod
    def get_all(active_only=False):
        from app.firebase import db
        if db is None: return []
        query = db.collection("causes")
        if active_only:
            query = query.where("active", "==", True)
        docs = query.order_by("created_at", direction="DESCENDING").stream()
        return [Cause(id=doc.id, **doc.to_dict()) for doc in docs]

    @staticmethod
    def get_by_id(cause_id):
        from app.firebase import db
        if not cause_id or db is None: return None
        doc = db.collection("causes").document(cause_id).get()
        if doc.exists:
            return Cause(id=doc.id, **doc.to_dict())
        return None

    @staticmethod
    def get_by_slug(slug):
        from app.firebase import db
        if not slug or db is None: return None
        docs = db.collection("causes").where("slug", "==", slug).limit(1).stream()
        for doc in docs:
            return Cause(id=doc.id, **doc.to_dict())
        return None

    def save(self):
        from app.firebase import db
        if db is None: return None
        data = self.to_dict()
        if self.id:
            db.collection("causes").document(self.id).set(data)
        else:
            _, doc_ref = db.collection("causes").add(data)
            self.id = doc_ref.id
        return self

    def delete(self):
        from app.firebase import db
        if self.id and db:
            db.collection("causes").document(self.id).delete()
            return True
        return False

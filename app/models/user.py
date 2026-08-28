from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app.firebase import db
from datetime import datetime

class User(UserMixin):
    def __init__(self, id, name, email, password_hash, role="EDITOR", active=True, created_at=None):
        self.id = id
        self.name = name
        self.email = email
        self.password_hash = password_hash
        self.role = role
        self.active = active
        self.created_at = created_at or datetime.now()

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        return {
            "name": self.name,
            "email": self.email,
            "password_hash": self.password_hash,
            "role": self.role,
            "active": self.active,
            "created_at": self.created_at
        }

    @staticmethod
    def get_by_id(user_id):
        if not user_id: return None
        doc = db.collection("users").document(user_id).get()
        if doc.exists:
            data = doc.to_dict()
            return User(id=doc.id, **data)
        return None

    @staticmethod
    def get_by_email(email):
        docs = db.collection("users").where("email", "==", email).limit(1).stream()
        for doc in docs:
            data = doc.to_dict()
            return User(id=doc.id, **data)
        return None

    def save(self):
        if self.id:
            db.collection("users").document(self.id).set(self.to_dict())
        else:
            _, doc_ref = db.collection("users").add(self.to_dict())
            self.id = doc_ref.id
        return self

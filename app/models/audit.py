from app.firebase import db
from datetime import datetime

class AuditLog:
    def __init__(self, id=None, user_id=None, action=None, entity=None, entity_id=None, created_at=None):
        self.id = id
        self.user_id = user_id
        self.action = action
        self.entity = entity
        self.entity_id = entity_id
        self.created_at = created_at or datetime.now()

    def to_dict(self):
        return {
            "user_id": self.user_id,
            "action": self.action,
            "entity": self.entity,
            "entity_id": self.entity_id,
            "created_at": self.created_at
        }

    def save(self):
        if self.id:
            db.collection("audit_logs").document(self.id).set(self.to_dict())
        else:
            _, doc_ref = db.collection("audit_logs").add(self.to_dict())
            self.id = doc_ref.id
        return self

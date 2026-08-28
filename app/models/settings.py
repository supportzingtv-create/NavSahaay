from datetime import datetime

class Setting:
    def __init__(self, key, value, created_at=None, updated_at=None):
        self.key = key
        self.value = value
        self.created_at = created_at or datetime.now()
        self.updated_at = updated_at or datetime.now()

    def to_dict(self):
        return {
            "key": self.key,
            "value": self.value,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }

    @staticmethod
    def get(key, default=None):
        from app.firebase import db
        if db is None: return default
        doc = db.collection("settings").document(key).get()
        if doc.exists:
            return doc.to_dict().get("value", default)
        return default

    @staticmethod
    def set(key, value):
        from app.firebase import db
        if db is None: return False
        db.collection("settings").document(key).set({
            "key": key,
            "value": value,
            "updated_at": datetime.now()
        }, merge=True)
        return True

    @staticmethod
    def get_slider_items():
        return Setting.get("hero_slider", [])

    @staticmethod
    def set_slider_items(items):
        return Setting.set("hero_slider", items)

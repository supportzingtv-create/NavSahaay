from app.firebase import db
from datetime import datetime

class Donation:
    def __init__(self, id=None, donation_id=None, receipt_number=None, donor_name=None,
                 email=None, phone=None, address=None, pan=None, amount=0,
                 frequency="ONE_TIME", cause=None, anonymous=False,
                 payment_method="MANUAL", status="PENDING", created_at=None):
        self.id = id
        self.donation_id = donation_id
        self.receipt_number = receipt_number
        self.donor_name = donor_name
        self.email = email
        self.phone = phone
        self.address = address
        self.pan = pan
        self.amount = amount
        self.frequency = frequency
        self.cause = cause
        self.anonymous = anonymous
        self.payment_method = payment_method
        self.status = status
        self.created_at = created_at or datetime.now()

    def to_dict(self):
        return {
            "donation_id": self.donation_id,
            "receipt_number": self.receipt_number,
            "donor_name": self.donor_name,
            "email": self.email,
            "phone": self.phone,
            "address": self.address,
            "pan": self.pan,
            "amount": self.amount,
            "frequency": self.frequency,
            "cause": self.cause,
            "anonymous": self.anonymous,
            "payment_method": self.payment_method,
            "status": self.status,
            "created_at": self.created_at
        }

    @staticmethod
    def get_by_id(donation_id_str):
        doc = db.collection("donations").document(donation_id_str).get()
        if doc.exists:
            return Donation(id=doc.id, **doc.to_dict())
        return None

    @staticmethod
    def count():
        # Firestore doesn't have a direct count() like SQL, but for small datasets we can stream
        # For production, we might want a counter document.
        return len(db.collection("donations").get())

    @staticmethod
    def get_recent(limit=8):
        docs = db.collection("donations").order_by("created_at", direction="DESCENDING").limit(limit).stream()
        return [Donation(id=doc.id, **doc.to_dict()) for doc in docs]

    @staticmethod
    def get_all():
        docs = db.collection("donations").order_by("created_at", direction="DESCENDING").stream()
        return [Donation(id=doc.id, **doc.to_dict()) for doc in docs]

    def save(self):
        if self.id:
            db.collection("donations").document(self.id).set(self.to_dict())
        else:
            _, doc_ref = db.collection("donations").add(self.to_dict())
            self.id = doc_ref.id
        return self

from app import db

class Donation(db.Model):
    __tablename__ = "donations"
    id = db.Column(db.Integer, primary_key=True)
    donation_id = db.Column(db.String(40), unique=True, nullable=False, index=True)
    receipt_number = db.Column(db.String(50), unique=True, nullable=True)
    donor_name = db.Column(db.String(160), nullable=False)
    email = db.Column(db.String(160), nullable=False)
    phone = db.Column(db.String(30), nullable=False)
    address = db.Column(db.Text, nullable=False)
    pan = db.Column(db.String(20), nullable=True)
    amount = db.Column(db.Numeric(12,2), nullable=False)
    frequency = db.Column(db.Enum("ONE_TIME", "MONTHLY", "YEARLY"), nullable=False)
    cause = db.Column(db.String(80), nullable=False)
    anonymous = db.Column(db.Boolean, default=False)
    payment_method = db.Column(db.String(50), default="MANUAL")
    status = db.Column(db.Enum("PENDING", "VERIFIED", "CANCELLED"), default="PENDING")
    created_at = db.Column(db.DateTime, server_default=db.func.now())

from app import db

class Volunteer(db.Model):
    __tablename__ = "volunteers"
    id = db.Column(db.Integer, primary_key=True)
    reference_id = db.Column(db.String(40), unique=True, nullable=False)
    name = db.Column(db.String(160), nullable=False)
    email = db.Column(db.String(160), nullable=False)
    phone = db.Column(db.String(30), nullable=False)
    city = db.Column(db.String(100), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    interest = db.Column(db.String(80), nullable=False)
    availability = db.Column(db.String(50), nullable=False)
    skills = db.Column(db.Text)
    experience = db.Column(db.Text)
    source = db.Column(db.String(120))
    status = db.Column(db.Enum("NEW", "CONTACTED", "APPROVED", "REJECTED"), default="NEW")
    created_at = db.Column(db.DateTime, server_default=db.func.now())

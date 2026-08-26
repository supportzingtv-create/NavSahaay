from app import db

class Contact(db.Model):
    __tablename__ = "contacts"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(160), nullable=False)
    email = db.Column(db.String(160), nullable=False)
    subject = db.Column(db.String(220), nullable=False)
    message = db.Column(db.Text, nullable=False)
    status = db.Column(db.Enum("NEW", "IN_PROGRESS", "CLOSED"), default="NEW")
    created_at = db.Column(db.DateTime, server_default=db.func.now())

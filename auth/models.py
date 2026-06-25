from db.extensions import db
from datetime import datetime

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    public_id = db.Column(db.String(50), unique=True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(70), unique=True)
    date_created=db.Column(db.DateTime, default=datetime.now())
    is_verified=db.Column(db.Boolean, default=False)
    password = db.Column(db.String(180))
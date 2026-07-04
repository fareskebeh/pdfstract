from db.extensions import db
from enum import Enum
from sqlalchemy import JSON

class Plan(db.Model):
    __tablename__='plans'

    id= db.Column(db.Integer, primary_key=True)
    name= db.Column(db.String(50))
    price_cents = db.Column(db.Integer)
    features=db.Column(JSON)
from db.extensions import db
from datetime import datetime
from keymanager.models import ApiKey
from sqlalchemy.ext.hybrid import hybrid_property

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(70), unique=True)
    date_created=db.Column(db.DateTime, default=datetime.now())
    is_verified=db.Column(db.Boolean, default=False)
    password_hash = db.Column(db.String(255))

    @hybrid_property
    def key_count(self):
        return db.session.query(db.func.count(ApiKey.id)).filter(ApiKey.user_id == self.id).scalar()
from flask_login import UserMixin
from .database import db
from uuid import uuid4

class Pac2User(UserMixin, db.Model):
    __tablename__ = "pac2user"

    id = db.Column(db.String(36), primary_key=True, default=str(uuid4()))
    username = db.Column(db.String(36), unique=True, nullable=False)
    password = db.Column(db.String, nullable=False)


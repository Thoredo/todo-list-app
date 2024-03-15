from datetime import datetime, timezone
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

db = SQLAlchemy()


class Users(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), nullable=False, unique=True)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    full_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False, unique=True)
    date_added = db.Column(db.DateTime, default=datetime.now(timezone.utc))

    password_hash = db.Column(db.String(128))

    # User can have many lists
    lists = db.relationship("List", backref="creator")

    @property
    def password(self):
        raise AttributeError("password is not a readable attribute!")

    def __repr__(self):
        return "<Name %r>" % self.first_name


class Lists(db.Model):
    # Add later list_name and group_id
    list_id = db.Column(db.Integer, primary_key=True)
    list_owner_id = db.Column(db.Integer, db.ForeignKey("users.id"))

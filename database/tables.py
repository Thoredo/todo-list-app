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

    lists = db.relationship("Lists", backref="creator")
    groups = db.relationship("GroupMembers", backref="group")

    @property
    def password(self):
        raise AttributeError("password is not a readable attribute!")

    def __repr__(self):
        return "<Name %r>" % self.first_name


class Lists(db.Model):
    # Add later group_id
    list_id = db.Column(db.Integer, primary_key=True)
    list_name = db.Column(db.String(100), nullable=False)
    list_owner_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    group_id = db.Column(db.Integer, db.ForeignKey("list_groups.group_id"))


class Groups(db.Model):
    __tablename__ = "list_groups"

    group_id = db.Column(db.Integer, primary_key=True)

    connected_list = db.relationship("Lists", backref="group")
    members = db.relationship("GroupMembers", backref="member")


class GroupMembers(db.Model):
    __tablename__ = "group_members"

    id = db.Column(db.Integer, primary_key=True)
    group_id = db.Column(db.Integer, db.ForeignKey("list_groups.group_id"))
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))

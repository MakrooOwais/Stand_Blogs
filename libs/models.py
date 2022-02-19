from __init__ import db
from flask_login import UserMixin


class User(UserMixin, db.Model):
    __tablename__ = 'users'
    Id = db.Column(
        db.Integer,
        primary_key=True
    )
    user_name = db.Column(
        db.String(100),
        nullable=False,
        unique=True
    ) 
    password = db.Column(
        db.String(80),
        primary_key=False,
        unique=False,
        nullable=False
	)
    picture = db.Column(
        db.String(80),
        primary_key=False,
    )

    def __repr__(self):
        return '<User {}>'.format(self.user_name)

    def get_id(self):
           return (self.Id)

class Blogs(db.Model):
    __tablename__ = 'blogs'
    Id = db.Column(
        db.Integer,
        primary_key=True
    )
    title = db.Column(
        db.String(100),
        nullable=False,
        unique=True
    )
    content = db.Column(
        db.String(1000),
        primary_key=False,
        unique=False,
        nullable=False
	)
    author = db.Column(
        db.String(100),
        nullable=False,
        unique=True
    )
    date_ = db.Column(
        db.String(100),
        nullable=False,
        unique=True
    )
    image = db.Column(
        db.String(100),
        nullable=False,
        unique=True
    )
    genre = db.Column(
        db.String(50),
        nullable=False,
        unique=True
    )
    comments = db.Column(
        db.String(1000),
        nullable=False,
        unique=True
    )
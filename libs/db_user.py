from libs.models import User
from __init__ import db

def add_user(username, password, picture):
    new_user = User(username=username, password=password, picture=picture)
    db.session.add(new_user)
    db.session.commit()
    return new_user

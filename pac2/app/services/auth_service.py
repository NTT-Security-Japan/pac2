from app.models import db, Pac2User
from werkzeug.security import generate_password_hash
from uuid import uuid4

def add_user(username, password)->bool:
    if not get_user_by_username(username):
        hashed_password = generate_password_hash(password)
        id = str(uuid4())
        new_user = Pac2User(id=id, username=username, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        return True
    else:
        return False

def get_user_by_id(user_id):
    return Pac2User.query.get(user_id)

def get_all_users():
    return Pac2User.query.all()

def get_user_by_username(username):
    return Pac2User.query.filter_by(username=username).first()

def update_password(user_id, new_password):
    user = Pac2User.query.get(user_id)
    if user:
        user.password = generate_password_hash(new_password)
        db.session.commit()

def delete_user(user_id):
    user = Pac2User.query.get(user_id)
    if user:
        db.session.delete(user)
        db.session.commit()
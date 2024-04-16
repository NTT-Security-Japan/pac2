from datetime import datetime
from app.models import db, User

# Create


def create_user(user_id: str, username, user_principal_name, tenant_id, email):

    user = User(
        user_id=user_id,
        username=username,
        user_principal_name=user_principal_name,
        tenant_id=tenant_id,
        email=email
    )
    db.session.add(user)
    db.session.commit()
    return user

# Read


def get_user_by_id(user_id):
    return User.query.get(user_id)


def get_all_users():
    return User.query.all()

# Update


def update_user(user_id, **kwargs):
    user: User = User.query.get(user_id)
    if user:
        for key, value in kwargs.items():
            if hasattr(user, key):
                setattr(user, key, value)
        user.updated_at = datetime.utcnow()
        db.session.commit()
    return user

# Delete


def delete_user(user_id):
    user = User.query.get(user_id)
    if user:
        db.session.delete(user)
        db.session.commit()

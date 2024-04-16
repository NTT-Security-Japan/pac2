from datetime import datetime
from .database import db


class User(db.Model):
    """
    ユーザーを管理するスキーマ
    """
    user_id = db.Column(db.String, primary_key=True, nullable=False)
    username = db.Column(db.String)
    user_principal_name = db.Column(db.String)
    tenant_id = db.Column(db.String)
    email = db.Column(db.String)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow)

    connections = db.relationship(
        "Connection", backref="user", uselist=False, lazy=True)
    environments = db.relationship(
        "Environment", backref="user", uselist=False, lazy=True)
    flowmanagement = db.relationship(
        "FlowManagement", backref="user", uselist=True, lazy=True)
    teams = db.relationship("Teams", backref="user", uselist=True, lazy=True)
    chat_user = db.relationship(
        "ChatUser", backref="user", uselist=True, lazy=True)

    def __repr__(self):
        return f"<User uuid:{self.user_id}, user:{self.username}>"


class Connection(db.Model):
    """
    PowerAutomateの接続情報を管理するテーブルスキーマ
    """
    user_id = db.Column(db.String, db.ForeignKey(
        'user.user_id'), primary_key=True, unique=True)
    data = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow)


class Environment(db.Model):
    """
    PowerAutomateの環境情報を管理するテーブルスキーマ
    """
    user_id = db.Column(db.String, db.ForeignKey(
        'user.user_id'), primary_key=True, unique=True)
    data = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow)

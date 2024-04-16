from datetime import datetime
from .database import db


class Teams(db.Model):
    """
    Teamsの情報を管理するテーブルスキーマ
    """
    id = db.Column(db.Integer, primary_key=True)
    teams_id = db.Column(db.String(36), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey(
        'user.user_id'), nullable=False)
    display_name = db.Column(db.Text)
    description = db.Column(db.Text)
    tenant_id = db.Column(db.String(36))
    is_archived = db.Column(db.Boolean)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow)
    channels = db.relationship(
        "Channel", backref="teams", uselist=True, lazy=True)
    messages = db.relationship(
        "Message", backref="teams", uselist=True, lazy=True)

    def __repr__(self):
        return f"<Teams id:{self.teams_id}, user:{self.user_id}>"


class Channel(db.Model):
    """
    Teamsのチャンネル情報を管理するテーブルスキーマ
    """
    id = db.Column(db.Integer, primary_key=True)
    channel_id = db.Column(db.Text, unique=True, nullable=False)
    teams_id = db.Column(db.String(36), db.ForeignKey(
        'teams.teams_id'), nullable=False)
    created_datetime = db.Column(db.String(24), nullable=True)
    display_name = db.Column(db.Text, nullable=True)
    description = db.Column(db.Text, nullable=True)
    email = db.Column(db.String(128), nullable=True)
    tenant_id = db.Column(db.String(36), nullable=True)
    weburl = db.Column(db.Text, nullable=True)
    membership_type = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow)
    messages = db.relationship(
        "Message", backref="channel", uselist=True, lazy=True)


class Message(db.Model):
    """
    Teamsのチャンネル内のメッセージを管理するテーブルスキーマ
    """
    id = db.Column(db.Integer, primary_key=True)
    message_id = db.Column(db.Text, unique=True)
    etag = db.Column(db.Text)
    message_type = db.Column(db.Text)
    create_datetime = db.Column(db.Text)
    last_modified_datetime = db.Column(db.Text)
    importance = db.Column(db.Text)
    weburl = db.Column(db.Text)
    locale = db.Column(db.Text)
    subject = db.Column(db.Text)
    from_user = db.Column(db.Text)  # JSON
    body = db.Column(db.Text)  # JSON
    attachments = db.Column(db.Text)  # JSON
    mentions = db.Column(db.Text)  # JSON
    reactions = db.Column(db.Text)  # JSON
    data = db.Column(db.Text)  # message_raw_data
    teams_id = db.Column(db.String(36), db.ForeignKey(
        'teams.teams_id'), nullable=False)
    channel_id = db.Column(db.Text, db.ForeignKey(
        'channel.channel_id'),  nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow)


class Chat(db.Model):
    """
    Teamsのチャット情報を管理するテーブルスキーマ
    """
    chat_id = db.Column(db.Text, unique=True, primary_key=True, nullable=False)
    topic = db.Column(db.Text)
    created_datetime = db.Column(db.String(24), nullable=True)
    lastUpdated_datetime = db.Column(db.String(24), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow)

    chat_user = db.relationship(
        "ChatUser", backref="chat", uselist=True, lazy=True)


class ChatUser(db.Model):
    __tablename__ = "chat_user"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String, db.ForeignKey('user.user_id'))
    chat_id = db.Column(db.String, db.ForeignKey('chat.chat_id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow)
    __table_args__ = (db.UniqueConstraint(
        'user_id', 'chat_id', name='unique_user_chat'),)

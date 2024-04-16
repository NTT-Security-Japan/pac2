from datetime import datetime
from .database import db


class FlowManagement(db.Model):
    """
    ユーザーのFlowManagement Connectionを管理するスキーマ
    """
    flowmanagement_id = db.Column(db.Text, primary_key=True, nullable=False)
    user_id = db.Column(db.String, db.ForeignKey(
        'user.user_id'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow)

    client = db.relationship(
        "Client", backref="flow_management", uselist=True, lazy=True)

    def get_user(self):
        """
        このFlowManagementに関連するUserのエントリーを取得
        """
        return self.user

from datetime import datetime
from .database import db
from uuid import uuid4


class Client(db.Model):
    """
    C2セッションを管理するテーブルスキーマ
    """
    client_id = db.Column(db.String(36), primary_key=True,
                          default=str(uuid4()))
    xor_key = db.Column(db.Text, nullable=True)
    is_encoded = db.Column(db.Boolean, nullable=False, default=True)
    method = db.Column(db.String, nullable=False)
    c2_connection = db.Column(db.String, nullable=False)
    last_payload = db.Column(db.Text, nullable=True)
    flowmanagement_id = db.Column(db.Text, db.ForeignKey(
        'flow_management.flowmanagement_id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow)

    tasks = db.relationship("Task", backref="client", uselist=False, lazy=True)

    def get_flowmanagement(self):
        """
        このClientに関連するFlowManagementのエントリーを取得
        """
        return self.flow_management

    def get_user(self):
        """
        このClientに関連するUserのエントリーを取得
        """
        from .flowmanagement import FlowManagement  # Lazy import
        flowmanagement: FlowManagement = self.get_flowmanagement()
        return flowmanagement.user if flowmanagement else None

    def get_connection(self):
        """
        このClientに関連するUserのConectionを取得
        """
        from .user import User  # Lazy import
        user: User = self.get_user()
        return user.connections if user else None

    def __repr__(self):
        from .user import User  # Lazy import
        user: User = self.get_user()
        return f"<Client id:{self.client_id}, user:{user.username if user else ''}>"

    def to_json(self):
        from .user import User  # Lazy import
        user: User = self.get_user()
        return {
            'client_id': self.client_id,
            'method': self.method,
            'is_encoded': self.is_encoded,
            'username': user.username if user else "",
            'email': user.email if user else "",
            'user_principal_name': user.user_principal_name if user else "",
            'user_uuid': user.user_id if user else "",
            'tenant_id': user.tenant_id if user else "",
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
        }

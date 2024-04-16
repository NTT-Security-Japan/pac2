from datetime import datetime
from .database import db
from uuid import uuid4
import json


class Task(db.Model):
    """
    タスク管理するテーブルスキーマ
    - task_type: task_type to run
    - task_args: expects json strings
    - state:
        submitted -> submitted to database 
        processing -> payload has generated
        finished -> payload has executed on powerautomate platform
        timeout -> timeouted after processing
    """
    task_id = db.Column(db.String(36), primary_key=True, default=str(uuid4()))
    client_id = db.Column(db.String(36), db.ForeignKey('client.client_id'), nullable=False)
    hash = db.Column(db.String(36), nullable=False)
    task_type = db.Column(db.String, nullable=False)
    task_args = db.Column(db.String, nullable=True)
    task_raw = db.Column(db.String, nullable=True)
    state = db.Column(db.String(16), nullable=False, default="submitted")
    created_at = db.Column(db.DateTime, default=datetime.utcnow())
    processed_at = db.Column(db.DateTime, nullable=True)
    finished_at = db.Column(db.DateTime, nullable=True)
    updated_at = db.Column(db.DateTime, nullable=True)

    def to_json(self):
        return {
            "task_id": self.task_id,
            "client_id": self.client_id,
            "hash": self.hash,
            "task_type": self.task_type,
            "task_args": json.loads(self.task_args),
            "task_raw": json.loads(self.task_raw),
            "state": self.state,
            "created_at": self.created_at,
            "processed_at": self.processed_at,
            "finished_at": self.finished_at,
            "updated_at": self.updated_at
        }

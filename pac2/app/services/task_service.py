from datetime import datetime
import json
from hashlib import md5
from uuid import uuid4
from typing import List

from app.services import client_service
from app.models import db
from app.models import Task


def task_hash(task_type: str, task_args: dict, task_raw: dict={}):
    contents = task_type + json.dumps(task_args) + json.dumps(task_raw)
    return md5(bytes(contents, "utf-8")).hexdigest()

# Create


def create_task(client_id: str, task_type: str, task_args: dict = {}, task_raw: dict = {}, state=None):
    # validate if client_id exists
    client = client_service.get_client_by_id(client_id)
    if not client:
        return None

    new_task = Task(
        task_id=str(uuid4()),
        client_id=client_id,
        hash=task_hash(task_type, task_args),
        task_type=task_type,
        task_args=json.dumps(task_args),
        task_raw=json.dumps(task_raw),
        state=state
    )
    db.session.add(new_task)
    db.session.commit()
    return new_task

# Read


def get_all_tasks():
    return Task.query.all()


def get_task_by_id(task_id):
    return Task.query.get(task_id)


def get_tasks_by_hash(hash) -> List[Task]:
    return Task.query.filter_by(hash=hash).all()


def get_tasks_by_client_id(client_id) -> List[Task]:
    return Task.query.filter_by(client_id=client_id).all()


def get_tasks_by_client_id_and_state(client_id, state) -> List[Task]:
    return Task.query.filter_by(client_id=client_id, state=state).all()

# Update


def update_task(task_id, **kwargs):
    task = get_task_by_id(task_id)

    if not task:
        return None

    for key, value in kwargs.items():
        if hasattr(task, key):
            setattr(task, key, value)

    task.updated_at = datetime.utcnow()
    db.session.commit()
    return task


def task_finished(task_id):
    task = get_task_by_id(task_id)

    if not task:
        return None

    task.updated_at = datetime.utcnow()
    task.finished_at = datetime.utcnow()
    task.state = "finished"
    db.session.commit()
    return task


def task_processing(task_id,state='processing'):
    task = get_task_by_id(task_id)

    if not task:
        return None

    task.updated_at = datetime.utcnow()
    task.processed_at = datetime.utcnow()
    task.state = state
    db.session.commit()
    return task


def task_timeout(task_id):
    task = get_task_by_id(task_id)

    if not task:
        return None

    task.updated_at = datetime.utcnow()
    task.state = "timeout"
    db.session.commit()
    return task

# Delete


def delete_task(task_id):
    task = get_task_by_id(task_id)

    if not task:
        return None

    db.session.delete(task)
    db.session.commit()
    return task

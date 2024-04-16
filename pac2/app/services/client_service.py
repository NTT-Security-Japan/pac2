from typing import List
from datetime import datetime
from uuid import uuid4
from random import randint
from app.models import db, Client

# Create


def create_client(flowmanagement_id: str, method: str, c2_connection: str, xor_key: str = None, is_encoded: bool = True, last_payload: str = None):
    new_client = Client(
        client_id=str(uuid4()),
        method=method,
        c2_connection=c2_connection,
        xor_key=xor_key,
        is_encoded=is_encoded,
        last_payload=last_payload,
        flowmanagement_id=flowmanagement_id
    )
    db.session.add(new_client)
    db.session.commit()
    return new_client

# Read


def get_client_by_id(client_id) -> Client:
    return Client.query.get(client_id)


def get_client_data_in_json(client_id):
    client = Client.query.get(client_id)
    return client.to_json() if client else {}


def get_all_clients() -> List[Client]:
    return Client.query.all()


def get_all_clients_in_json():
    data = []
    for client in Client.query.all():
        data.append(client.to_json())
    return data

# Update


def update_client(client_id, **kwargs):
    client = Client.query.get(client_id)
    if client:
        for key, value in kwargs.items():
            if key in ["is_encoded", "method"]:  # set immutable columns.
                continue
            setattr(client, key, value)
        client.updated_at = datetime.utcnow()
        db.session.commit()
    return client

# Delete


def delete_client(client_id):
    client = Client.query.get(client_id)
    if client:
        db.session.delete(client)
        db.session.commit()

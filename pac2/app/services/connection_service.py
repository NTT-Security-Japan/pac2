from datetime import datetime
from app.models import db, Connection


# CREATE
def create_connection(user_id, data):
    """
    Creates and adds a new Connection to the database.

    Parameters:
    - user_id (str): Client ID the connection is associated with.
    - data (str): Data related to the connection.

    Returns:
    - Connection: Newly created Connection object.
    """
    connection = Connection(user_id=user_id, data=data)
    db.session.add(connection)
    db.session.commit()
    return connection

# READ


def get_connection_by_id(user_id):
    """
    Retrieves a Connection from the database by its ID.

    Parameters:
    - user_id (int): ID of the connection.

    Returns:
    - Connection: Connection object or None if not found.
    """
    return Connection.query.get(user_id)

# UPDATE


def update_connection(user_id, data=None):
    """
    Updates attributes of a Connection in the database.

    Parameters:
    - user_id (int): ID of the connection to be updated.
    - data (str, optional): New data for the connection.

    Returns:
    - Connection: Updated Connection object or None if not found.
    """
    connection = get_connection_by_id(user_id)
    if connection:
        if data:
            connection.data = data
        connection.updated_at = datetime.utcnow()
        db.session.commit()
    return connection

# DELETE


def delete_connection(user_id):
    """
    Deletes a Connection from the database.

    Parameters:
    - user_id (int): ID of the connection to be deleted.

    Side effects:
    - Removes the connection from the database.
    """
    connection = get_connection_by_id(user_id)
    if connection:
        db.session.delete(connection)
        db.session.commit()

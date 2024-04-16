from datetime import datetime
from app.models import db, Environment

# CREATE


def create_environment(user_id, data):
    """
    Creates and adds a new Environment to the database.

    Parameters:
    - user_id (str): user ID the environment is associated with.
    - data (str): Data related to the environment.

    Returns:
    - Environment: Newly created Environment object.
    """
    environment = Environment(user_id=user_id, data=data)
    db.session.add(environment)
    db.session.commit()
    return environment

# READ


def get_environment_by_id(user_id):
    """
    Retrieves an Environment from the database by its ID.

    Parameters:
    - user_id (int): ID of the environment.

    Returns:
    - Environment: Environment object or None if not found.
    """
    return Environment.query.get(user_id)
# UPDATE


def update_environment(user_id, data=None):
    """
    Updates attributes of an Environment in the database.

    Parameters:
    - user_id (int): ID of the environment to be updated.
    - data (str, optional): New data for the environment.

    Returns:
    - Environment: Updated Environment object or None if not found.
    """
    environment = get_environment_by_id(user_id)
    if environment:
        if data:
            environment.data = data
        environment.updated_at = datetime.utcnow()
        db.session.commit()
    return environment

# DELETE


def delete_environment(user_id):
    """
    Deletes an Environment from the database.

    Parameters:
    - user_id (int): ID of the environment to be deleted.

    Side effects:
    - Removes the environment from the database.
    """
    environment = get_environment_by_id(user_id)
    if environment:
        db.session.delete(environment)
        db.session.commit()

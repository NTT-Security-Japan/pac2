from datetime import datetime
from app.models import db, FlowManagement

# Create


def create_flowmanagement(flowmanagement_id: str, user_id=None):
    flowmanagement = FlowManagement(
        flowmanagement_id=flowmanagement_id,
        user_id=user_id
    )
    db.session.add(flowmanagement)
    db.session.commit()
    return flowmanagement

# Read


def get_flowmanagement_by_id(flowmanagement_id):
    return FlowManagement.query.get(flowmanagement_id)


def get_all_flowmanagements():
    return FlowManagement.query.all()

# Update


def update_flowmanagement(flowmanagement_id, user_id=None):
    flowmanagement = FlowManagement.query.get(flowmanagement_id)
    if flowmanagement:
        if user_id:
            flowmanagement.user_id = user_id
        flowmanagement.updated_at = datetime.utcnow()
        db.session.commit()
    return flowmanagement

# Delete


def delete_flowmanagement(flowmanagement_id):
    flowmanagement = FlowManagement.query.get(flowmanagement_id)
    if flowmanagement:
        db.session.delete(flowmanagement)
        db.session.commit()

# Getting the user for a particular flow management


def get_user_for_flowmanagement(flowmanagement_id):
    flowmanagement = FlowManagement.query.get(flowmanagement_id)
    if flowmanagement:
        return flowmanagement.get_user()


if __name__ == "__main__":
    db.create_all()

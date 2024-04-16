import os
from datetime import datetime, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from app.models import User,Task

SQLALCHEMY_DATABASE_URI = "sqlite:///" + os.path.join(os.path.dirname(__file__), "data.db")

engine = create_engine(SQLALCHEMY_DATABASE_URI)
session_factory = sessionmaker(bind=engine)
Session = scoped_session(session_factory)

task = Session.query(Task).all()[0]
timeout_boarder = datetime.utcnow() - timedelta(minutes=10)
print(timeout_boarder , task.processed_at)
print(type(task.processed_at))
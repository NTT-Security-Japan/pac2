import os
import logging.handlers
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker


def init_db_session(DATABASE_URI):
    engine = create_engine(DATABASE_URI)
    session_factory = sessionmaker(bind=engine)
    return scoped_session(session_factory)

def init_log_listener(log_path, log_queue):
    logfile = os.path.join(log_path, 'worker.log')
    file_handler = logging.FileHandler(logfile)
    formatter = logging.Formatter('%(asctime)s [%(name)-12.12s] [%(levelname)-5.5s]  %(message)s')
    file_handler.setFormatter(formatter)
    log_listner = logging.handlers.QueueListener(log_queue,file_handler)
    log_listner.start()

def get_log_writer(log_queue):
    queue_hadler = logging.handlers.QueueHandler(log_queue)
    logger = logging.getLogger("Main")
    logger.addHandler(queue_hadler)
    logger.setLevel(logging.INFO)
    return logger
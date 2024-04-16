from typing import List
import os
import multiprocessing
import logging
import logging.handlers
from datetime import datetime, timedelta
from time import sleep
from .dropbox.config import init_db_session
from app.models import Client, Task


class MonitorTaskProcess(multiprocessing.Process):
    """
    Taskを監視し、開始10分経過し、終了していないタスクをtimeoutにする。
    """
    def __init__(self, log_queue, db_uri):
        super().__init__()
        self.log_queue = log_queue
        self.daemon = True
        self.running = True
        self.db_uri = db_uri
    
    def run(self):
        # setup logger
        queue_hadler = logging.handlers.QueueHandler(self.log_queue)
        logger = logging.getLogger(__class__.__name__)
        logger.addHandler(queue_hadler)
        logger.setLevel(logging.INFO)

        logger.info(f"{self.__class__.__name__} started.(Multiprocess ver.)")
        session = init_db_session(self.db_uri)
        while self.running:
            clients = session.query(Client).all()
            for client in clients:
                # set the state to "timeout" for unfinished tasks
                timeout_boarder = datetime.utcnow() - timedelta(minutes=10)
                expired_tasks:List[Task] = session.query(Task).filter(Task.client_id==client.client_id, Task.state=="processing", Task.processed_at < timeout_boarder).all()

                for task in expired_tasks:
                    task.updated_at = datetime.utcnow()
                    task.finished_at = datetime.utcnow()
                    task.state = "timeout"
                    session.commit()
                    logger.info(f"Task has timeouted. TaskID {task.task_id}")

            sleep(5)


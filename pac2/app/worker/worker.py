from typing import Dict
import os
import multiprocessing
from flask import Flask
from .monitortask import MonitorTaskProcess
from app.worker.dropbox import SetupClientProcess, PostDataProcess, PutPayloadProcess
from app.worker.dropbox.config import get_log_writer, init_log_listener

WORKER_PROCESSES = []
LOG_QUEUE = multiprocessing.Queue(-1)

def start_dropbox_worker(app: Flask):
    mount_path = app.config.get("DROPBOX_MOUNT_PATH")
    log_path = app.config.get("DROPBOX_LOG_PATH")
    pac2_exchange_path = app.config.get("DROPBOX_PAC2_ROOT")
    db_uri = app.config.get("SQLALCHEMY_DATABASE_URI")
    sleep_time = app.config.get("SLEEP_TIME", 60)
    jitter = app.config.get("JITTER", 10)
    has_approval = app.config.get("SET_APPROVE_ACTION", True)

    init_log_listener(log_path, LOG_QUEUE)

    dropbox_logger = get_log_writer(LOG_QUEUE)
    dropbox_logger.info("Dropbox handler started.")

    if not os.path.exists(mount_path):
        dropbox_logger.error("Dropbox is not mouted.")
        return

    if not os.path.exists(pac2_exchange_path):
        os.mkdir(pac2_exchange_path)
        dropbox_logger.info("Create pac2 root path for dropbox c2 communication.")

    WORKER_PROCESSES.append(MonitorTaskProcess(LOG_QUEUE,db_uri))
    WORKER_PROCESSES.append(SetupClientProcess(LOG_QUEUE, db_uri, pac2_exchange_path,sleep_time,jitter,has_approval))
    WORKER_PROCESSES.append(PostDataProcess(LOG_QUEUE, db_uri, pac2_exchange_path))
    WORKER_PROCESSES.append(PutPayloadProcess(LOG_QUEUE, db_uri, pac2_exchange_path,sleep_time,jitter,has_approval))

    for process in WORKER_PROCESSES:
        process.start()
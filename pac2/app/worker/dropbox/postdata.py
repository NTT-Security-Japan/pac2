
import os
import re
import glob
import json
import multiprocessing
import logging
from datetime import datetime
from time import sleep
from hashlib import md5
from .config import init_db_session
from app.models.client import Client
from app.models.task import Task
from app.worker.httpclient import HttpClient, resolve_urlpath


PAT_UUID4 = re.compile(
    r'^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$', re.IGNORECASE)

MAP_CONNECTION_CLINT = {}

def hash_file(filepath):
    with open(filepath,"r") as f:
        return md5(bytes(f.read(), "utf-8")).hexdigest()

class PostDataProcess(multiprocessing.Process):
    """
    Dropboxがマウントされたフォルダを監視し、実行されたTask結果をWebAPIにPOSTする。
    """
    def __init__(self, log_queue, db_uri, monitor_path):
        super().__init__()
        self.log_queue = log_queue
        self.daemon = True
        self.running = True
        self.monitor_path = monitor_path
        self.db_uri = db_uri
    
    def run(self):
        # setup logger
        queue_hadler = logging.handlers.QueueHandler(self.log_queue)
        logger = logging.getLogger(__class__.__name__)
        logger.addHandler(queue_hadler)
        logger.setLevel(logging.INFO)
        logger.info(f"{self.__class__.__name__} started.(Multiprocess ver.)")
        session = init_db_session(self.db_uri)

        # init HTTP Client
        logger.debug("Init HTTP client.")
        httpclient = HttpClient()
        httpclient.wait_util_server_start()
        logger.debug("Server alive.")
        
        while self.running:
            clients = session.query(Client).all()
            for client in clients:
                if client.method != "dropbox":
                    continue
                logger.debug(f"Checking {client.client_id}")
                # set Pa-Clint-Id to headers
                httpclient.set_client_id(client.client_id)

                upload_path = os.path.join(self.monitor_path, client.client_id, "upload")

                # create client path
                if not os.path.exists(upload_path):
                    continue

                # post connection
                # only post when the data has changed.
                connections_path = os.path.join(upload_path, "connections.json")
                if os.path.exists(connections_path):
                    logger.debug(f"Found connections.json. {client.client_id}")
                    cur_hash = hash_file(connections_path)
                    prev_hash = MAP_CONNECTION_CLINT.get(client.client_id,"")
                    if cur_hash == prev_hash:
                        logger.debug(f"No change for connections.json.  {client.client_id}")
                    else:
                        httpclient.post_json_file("connections", connections_path)
                        logger.info(f"Post connections data. ClientID:{client.client_id}")
                        MAP_CONNECTION_CLINT[client.client_id] = cur_hash

                # post task results
                # file path is expected as {client_id}/upload/{task_id}-{idx}.json
                files = glob.glob(os.path.join(self.monitor_path, client.client_id, "upload", "*-*.json"))
                logger.debug(f"Found {len(files)} files to process. {client.client_id}")
                for filepath in files:
                    # extract task_id from filename
                    filename = filepath.split("/")[-1]
                    task_id, _ = filename.rsplit("-", 1)
                    if not PAT_UUID4.match(task_id):
                        continue
                    try:
                        data = None
                        with open(filepath, "r") as f:
                            data = json.load(f)
                            urlpath = resolve_urlpath(data["@odata.context"])
                        if not urlpath:
                            continue
                        httpclient.set_task_id(task_id)
                        res = httpclient.post_json_str(urlpath, json.dumps(data))
                        if res.status_code == 200:
                            logger.info(f"Post json data to /{urlpath}. ClientID:{client.client_id}")

                            # set task as finished
                            task = session.query(Task).filter(Task.task_id == task_id).first()

                            if task:
                                task.updated_at = datetime.utcnow()
                                task.finished_at = datetime.utcnow()
                                task.state = "finished"
                                session.commit()
                            else:
                                logger.warning(f"TaskID not found. {task_id}")

                            # remove processed file
                            try:
                                os.remove(filepath)
                            except BaseException:
                                logger.error(e)
                    except BaseException as e:
                        logger.error(e)
                        pass
                    # Delete Pa-Task-Id from headers
                    httpclient.remove_task_id()

            sleep(5)

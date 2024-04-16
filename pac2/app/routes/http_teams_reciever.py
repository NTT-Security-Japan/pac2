from flask import Blueprint, request, g, abort, jsonify
import json
import re
from urllib.parse import unquote
from app.utils.html import remove_img_tag
from flask import current_app as app
import os
from app.services import client_service, teams_service, task_service, user_service
from app.utils.logger import log_after_request, setup_logger

http_teams_reciever = Blueprint(
    "http_teams_reciever", __name__, template_folder="templates")

URL_PATTERN_CHANNLE_LIST = r"https://graph\.microsoft\.com/v1\.0/\$metadata#teams\('([a-fA-F0-9]{8}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{12})'\)/channels"
URL_PATTERN_MESSAGES = r"https://graph\.microsoft\.com/beta/\$metadata#teams\('([a-fA-F0-9]{8}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{12})'\)/channels\('([\w%:@.]+)'\)/messages"
URL_PATTERN_CHAT = r"https://graph\.microsoft\.com/v1\.0/\$metadata#chats\('([\w%:@.]+)'\)/members"

# Setup logging modules
log_path = os.path.abspath(os.path.join(
    __file__, "..", "..", "log", "c2_access.log"))
setup_logger("c2_access", log_path,)


@http_teams_reciever.before_request
def preprocess():
    """
    Teams関連のリクエストの前処理
    """
    if "azure-logic-apps/1.0" not in request.headers.get("User-Agent"):
        return abort(401)

    # HTTPヘッダ Pa-Client-Id, Pa-Task-Id
    g.client_id = request.headers.get("Pa-Client-Id", None)
    task_id = request.headers.get("Pa-Task-Id", None)

    # DBにセッション情報があるか確認する
    g.client = client_service.get_client_by_id(g.client_id)
    if not g.client:
        return abort(401)
    else:
        # セッションの最終更新を更新する
        g.client = client_service.update_client(g.client.client_id)
    g.client_id = g.client.client_id

    # task_idのステータスを更新する
    if task_id:
        task_service.task_finished(task_id)


@http_teams_reciever.route("/teams/team_list", methods=["POST"])
def teams_team_list():
    """
    Teamsのチーム一覧を受信するためのパス
    """
    result = {
        "result": "Failed",
    }

    data = request.get_json()
    user = g.client.get_user()
    if not user:
        result["reason"] = "User data does not exists."
        return jsonify(result), 406

    user_id = user.user_id

    # validation
    if data["@odata.context"] != "https://graph.microsoft.com/v1.0/$metadata#teams":
        result["reason"] = "Invalide data context."
        return jsonify(result), 406

    result["teams_id"] = []

    # jsonに含まれる所属Teamをそれぞれ追加
    for d in data["value"]:
        if not teams_service.get_team_by_teams_id(d["id"]):
            teams_service.create_team(user_id, d)
            result["teams_id"].append(d["id"])

    result["result"] = "Success"
    return jsonify(result), 200


@http_teams_reciever.route("/teams/channel_list", methods=["POST"])
def teams_channel_list():
    """
    Teamsのチャンネル一覧を受信するためのパス
    """
    result = {
        "result": "Failed",
    }

    data = request.get_json()

    # validation
    m = re.match(URL_PATTERN_CHANNLE_LIST, data["@odata.context"])
    if not m:
        result["reason"] = "Invalide data context."
        return jsonify(result), 406

    # extract Teams ID from metadata
    teams_id = m.groups()[0]
    if not teams_id:
        result["reason"] = "No teams_id"
        return jsonify(result), 406

    result["channel_id"] = []

    # jsonに含まれるchannelをそれぞれ追加
    for d in data["value"]:
        if not teams_service.get_channel_by_channel_id(d["id"]):
            teams_service.create_channel(teams_id, d)
            result["channel_id"].append(d["id"])

    result["result"] = "Success"
    return jsonify(result), 200


@http_teams_reciever.route("/teams/chat_list", methods=["POST"])
def teams_chat_list():
    """
    Teamsのチャット一覧を受信するためのパス
    """

    result = {
        "result": "Failed",
    }

    data = request.get_json()
    user = g.client.get_user()
    if not user:
        result["reason"] = "User data does not exists."
        return jsonify(result), 406

    user_id = user.user_id

    # validation
    if data["@odata.context"] != "https://graph.microsoft.com/beta/$metadata#chats":
        result["reason"] = "Invalide data context."
        return jsonify(result), 406

    result["chat_id"] = []

    # jsonに含まれるchatをそれぞれ追加
    for d in data["value"]:
        chat_id = d["id"]
        if not teams_service.get_chat_by_chat_id(chat_id):
            teams_service.create_chat(chat_id, **d)
            result["chat_id"].append(d["id"])
            teams_service.create_chatuser(chat_id, user_id)

    result["result"] = "Success"
    return jsonify(result), 200


@http_teams_reciever.route("/teams/chat_members", methods=["POST"])
def teams_chat_members():
    """
    Chatのメンバー一覧を受信するためのパス
    """
    result = {
        "result": "Failed",
    }

    data = request.get_json()
    user = g.client.get_user()
    if not user:
        result["reason"] = "User data does not exists."
        return jsonify(result), 406

    user_id = user.user_id
    # validation
    m = re.match(URL_PATTERN_CHAT, data["@odata.context"])
    if not m:
        result["reason"] = "Invalide data context."
        return jsonify(result), 406

    chat_id = unquote(m.groups()[0])

    # jsonに含まれるchatをそれぞれ追加
    for d in data["value"]:
        user_id = d.get("userId", "")
        username = d.get("displayName", "")
        email = d.get("email", "")
        tenant_id = d.get("tenantId", "")
        user_principal_name = d.get("userPrincipalName", "")
        if not user_service.get_user_by_id(user_id):
            user_service.create_user(
                user_id, username, user_principal_name, tenant_id, email)
        if not teams_service.get_chatuser(chat_id, user_id):
            teams_service.create_chatuser(chat_id, user_id)
    result["result"] = "Success"
    return jsonify(result), 200


@http_teams_reciever.route("/teams/messages", methods=["POST"])
def teams_messages():
    """
    Teamsのチャンネル内のメッセージを受信するためのパス
    """
    result = {
        "result": "Failed",
    }

    data = request.get_json()

    # validation
    m = re.match(URL_PATTERN_MESSAGES, data["@odata.context"])
    if not m:
        result["reason"] = "Invalide data context."
        return jsonify(result), 406

    result["message_id"] = []

    teams_id = m.groups()[0]
    channel_id = unquote(m.groups()[1])

    # jsonに含まれるmessageをそれぞれ追加
    for d in data["value"]:
        if not teams_service.get_message_by_message_id(d["id"]):
            # remove img tag which source contains "graph.microsoft.com"
            if d['body'].get("contentType", None) == "html":
                html = remove_img_tag(
                    d['body']['content'], "graph.microsoft.com")
                d['body']['content'] = html
            teams_service.create_message(teams_id, channel_id, d)
            result["message_id"].append(d["id"])

    result["result"] = "Success"
    return jsonify(result), 200


@http_teams_reciever.after_request
def postprocess(response):
    """
    リクエストの後処理（ログ）
    """
    return log_after_request(response, "c2_access")

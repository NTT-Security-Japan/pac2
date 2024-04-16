import re
import json
import requests
from time import sleep
from typing import Optional

URL_PATH_MAP = {
    "teams/team_list": r"^https://graph\.microsoft\.com/v1\.0/\$metadata#teams$",
    "teams/channel_list": r"^https://graph\.microsoft\.com/v1\.0/\$metadata#teams\('([a-fA-F0-9]{8}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{12})'\)/channels$",
    "teams/messages": r"^https://graph\.microsoft\.com/beta/\$metadata#teams\('([a-fA-F0-9]{8}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{12})'\)/channels\('([\w%:@.]+)'\)/messages$",
    "teams/chat_list": r"^https://graph\.microsoft\.com/beta/\$metadata#chats$",
    "teams/chat_members": r"^https://graph\.microsoft\.com/v1\.0/\$metadata#chats\('([\w%:@.]+)'\)/members$"
}


def resolve_urlpath(context: str) -> str:
    for urlpath, pattern in URL_PATH_MAP.items():
        if re.match(pattern, context):
            return urlpath
    return ""


class HttpClient:
    USER_AGENT = "azure-logic-apps/1.0"

    def __init__(self, pac2_host: str = "127.0.0.1", pac2_port: int = 9999, use_ssl=False):
        if use_ssl:
            self.url = f"https://{pac2_host}:{pac2_port}"
        else:
            self.url = f"http://{pac2_host}:{pac2_port}"
        self.headers = {
            "User-Agent": self.USER_AGENT,
            "Pa-Client-Id": "",
            "Content-Type": "application/json; charset=utf-8",
            "Content-Length": ""
        }

    def wait_util_server_start(self):
        cnt = 0
        while True:
            cnt += 1
            try:
                res = requests.get(self.url)
                if res.status_code == 200:
                    return True
            except requests.RequestException:
                pass
            if cnt > 30:
                raise TimeoutError("Failed to connect PAC2.")
            sleep(10)

    def set_client_id(self, client_id: str) -> None:
        self.headers["Pa-Client-Id"] = client_id

    def set_task_id(self, task_id: str) -> None:
        self.headers["Pa-Task-Id"] = task_id

    def remove_task_id(self) -> None:
        self.headers.pop("Pa-Task-Id", None)

    def post_json_str(self, urlpath: str, data: str) -> Optional[requests.Response]:
        if not data:
            return None
        self.headers["Content-Length"] = str(len(data))
        return requests.post(f"{self.url}/{urlpath}", headers=self.headers, data=data)

    def post_json_file(self, urlpath: str, filepath: str) -> Optional[requests.Response]:
        try:
            with open(filepath, "r") as f:
                data = json.load(f)
                data = json.dumps(data, ensure_ascii=False)
        except json.decoder.JSONDecodeError:
            return None
        return self.post_json_str(urlpath, data)

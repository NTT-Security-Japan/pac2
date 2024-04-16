from typing import Dict
from .teams import *

"""
How to add new payloads.
1. Create class which inherit BasePaload class.
2. Add annotations to __init__ method in inherited class.
3. Override generate_payload method.
4. Add new class to PAYLOAD_MODULES.
"""

PAYLOAD_MODULES: Dict[str, BasePayload] = {
    "CollectTeamsChannelPayload": CollectTeamsChannelPayload,
    "CollectTeamsMessagePayload": CollectTeamsMessagePayload,
    "CollectTeamsChatsPayload": CollectTeamsChatsPayload,
    "CollectTeamsChatMemberPayload": CollectTeamsChatMemberPayload
}

INPUT_TYPE_MAP = {
    "c2_url": "hidden",
    "client_id": "hidden",
    "teams_id": "list",
    "channel_id": "list",
    "message_id": "list",
    "chat_id": "list",
}

from abc import ABC, abstractmethod
from typing import Set

try:
    from CynanBotCommon.twitch.websocket.twitchWebsocketUser import \
        TwitchWebsocketUser
except:
    from twitch.websocket.twitchWebsocketUser import TwitchWebsocketUser


class TwitchWebsocketAllowedUsersRepositoryInterface(ABC):

    @abstractmethod
    async def getUsers(self) -> Set[TwitchWebsocketUser]:
        pass

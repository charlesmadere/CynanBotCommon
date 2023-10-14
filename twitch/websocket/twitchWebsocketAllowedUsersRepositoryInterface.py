from abc import abstractmethod
from typing import List

try:
    from CynanBotCommon.clearable import Clearable
    from CynanBotCommon.twitch.websocket.twitchWebsocketUser import \
        TwitchWebsocketUser
except:
    from clearable import Clearable

    from twitch.websocket.twitchWebsocketUser import TwitchWebsocketUser


class TwitchWebsocketAllowedUsersRepositoryInterface(Clearable):

    @abstractmethod
    async def getUsers(self) -> List[TwitchWebsocketUser]:
        pass

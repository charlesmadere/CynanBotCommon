from abc import ABC, abstractmethod
from typing import Optional

try:
    from CynanBotCommon.twitch.websocket.websocketDataBundle import \
        WebsocketDataBundle
except:
    from twitch.websocket.websocketDataBundle import WebsocketDataBundle


class TwitchWebsocketJsonMapperInterface(ABC):

    @abstractmethod
    async def toWebsocketDataBundle(self, message: Optional[str]) -> Optional[WebsocketDataBundle]:
        pass

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional

try:
    from CynanBotCommon.twitch.websocket.websocketCondition import \
        WebsocketCondition
    from CynanBotCommon.twitch.websocket.websocketDataBundle import \
        WebsocketDataBundle
    from CynanBotCommon.twitch.websocket.websocketReward import WebsocketReward
except:
    from twitch.websocket.websocketCondition import WebsocketCondition
    from twitch.websocket.websocketDataBundle import WebsocketDataBundle
    from twitch.websocket.websocketReward import WebsocketReward


class TwitchWebsocketJsonMapperInterface(ABC):

    @abstractmethod
    async def parseWebsocketCondition(self, conditionJson: Optional[Dict[str, Any]]) -> Optional[WebsocketCondition]:
        pass

    @abstractmethod
    async def parseWebsocketDataBundle(self, message: Optional[str]) -> Optional[WebsocketDataBundle]:
        pass

    @abstractmethod
    async def parseWebsocketReward(self, rewardJson: Optional[Dict[str, Any]]) -> Optional[WebsocketReward]:
        pass

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional

try:
    from CynanBotCommon.twitch.websocket.websocketCondition import \
        WebsocketCondition
    from CynanBotCommon.twitch.websocket.websocketDataBundle import \
        WebsocketDataBundle
    from CynanBotCommon.twitch.websocket.websocketEvent import WebsocketEvent
    from CynanBotCommon.twitch.websocket.websocketOutcome import \
        WebsocketOutcome
    from CynanBotCommon.twitch.websocket.websocketOutcomePredictor import \
        WebsocketOutcomePredictor
    from CynanBotCommon.twitch.websocket.websocketReward import WebsocketReward
    from CynanBotCommon.twitch.websocket.websocketSession import \
        WebsocketSession
    from CynanBotCommon.twitch.websocket.websocketSubscription import \
        WebsocketSubscription
except:
    from twitch.websocket.websocketCondition import WebsocketCondition
    from twitch.websocket.websocketDataBundle import WebsocketDataBundle
    from twitch.websocket.websocketEvent import WebsocketEvent
    from twitch.websocket.websocketOutcome import WebsocketOutcome
    from twitch.websocket.websocketOutcomePredictor import \
        WebsocketOutcomePredictor
    from twitch.websocket.websocketReward import WebsocketReward
    from twitch.websocket.websocketSession import WebsocketSession
    from twitch.websocket.websocketSubscription import WebsocketSubscription


class TwitchWebsocketJsonMapperInterface(ABC):

    @abstractmethod
    async def parseWebsocketCondition(self, conditionJson: Optional[Dict[str, Any]]) -> Optional[WebsocketCondition]:
        pass

    @abstractmethod
    async def parseWebsocketDataBundle(self, dataBundleJson: Optional[Dict[str, Any]]) -> Optional[WebsocketDataBundle]:
        pass

    @abstractmethod
    async def parseWebsocketEvent(self, eventJson: Optional[Dict[str, Any]]) -> Optional[WebsocketEvent]:
        pass

    @abstractmethod
    async def parseWebsocketOutcome(self, outcomeJson: Optional[Dict[str, Any]]) -> Optional[WebsocketOutcome]:
        pass

    @abstractmethod
    async def parseWebsocketOutcomePredictor(self, predictorJson: Optional[Dict[str, Any]]) -> Optional[WebsocketOutcomePredictor]:
        pass

    @abstractmethod
    async def parseWebsocketReward(self, rewardJson: Optional[Dict[str, Any]]) -> Optional[WebsocketReward]:
        pass

    @abstractmethod
    async def parseWebsocketSession(self, sessionJson: Optional[Dict[str, Any]]) -> Optional[WebsocketSession]:
        pass

    @abstractmethod
    async def parseWebsocketSubscription(self, subscriptionJson: Optional[Dict[str, Any]]) -> Optional[WebsocketSubscription]:
        pass

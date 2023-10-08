from abc import ABC, abstractmethod
from typing import Optional

try:
    from CynanBotCommon.twitch.websocket.twitchWebsocketClientListener import \
        TwitchWebsocketClientListener
except:
    from twitch.websocket.twitchWebsocketClientListener import \
        TwitchWebsocketClientListener


class TwitchWebsocketClientInterface(ABC):

    @abstractmethod
    def setListener(self, listener: Optional[TwitchWebsocketClientListener]):
        pass

    @abstractmethod
    def start(self):
        pass

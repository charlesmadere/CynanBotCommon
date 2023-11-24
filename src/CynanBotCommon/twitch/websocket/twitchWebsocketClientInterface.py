from abc import ABC, abstractmethod
from typing import Optional

try:
    from CynanBotCommon.twitch.websocket.twitchWebsocketDataBundleListener import \
        TwitchWebsocketDataBundleListener
except:
    from CynanBotCommon.twitch.websocket.twitchWebsocketDataBundleListener import \
        TwitchWebsocketDataBundleListener


class TwitchWebsocketClientInterface(ABC):

    @abstractmethod
    def setDataBundleListener(self, listener: Optional[TwitchWebsocketDataBundleListener]):
        pass

    @abstractmethod
    def start(self):
        pass

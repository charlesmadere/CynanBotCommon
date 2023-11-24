from abc import ABC, abstractmethod

try:
    from CynanBotCommon.twitch.websocket.websocketDataBundle import \
        WebsocketDataBundle
except:
    from twitch.websocket.websocketDataBundle import WebsocketDataBundle


class TwitchWebsocketDataBundleListener(ABC):

    @abstractmethod
    async def onNewWebsocketDataBundle(self, dataBundle: WebsocketDataBundle):
        pass

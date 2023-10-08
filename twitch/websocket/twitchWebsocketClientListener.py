from abc import ABC, abstractmethod

try:
    from CynanBotCommon.twitch.websocket.websocketDataBundle import \
        WebsocketDataBundle
except:
    from twitch.websocket.websocketDataBundle import WebsocketDataBundle


class TwitchWebsocketClientListener(ABC):

    @abstractmethod
    async def onTwitchWebsocketClientEvent(self, dataBundle: WebsocketDataBundle):
        pass

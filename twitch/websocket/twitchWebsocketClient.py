import asyncio
import queue
from queue import SimpleQueue
from typing import Optional

from CynanBotCommon.twitch.websocket.twitchWebsocketClientListener import \
    TwitchWebsocketClientListener

try:
    import CynanBotCommon.utils as utils
    from CynanBotCommon.backgroundTaskHelper import BackgroundTaskHelper
    from CynanBotCommon.timber.timberInterface import TimberInterface
    from CynanBotCommon.twitch.websocket.twitchWebsocketClientInterface import \
        TwitchWebsocketClientInterface
    from CynanBotCommon.twitch.websocket.twitchWebsocketClientListener import \
        TwitchWebsocketClientListener
    from CynanBotCommon.twitch.websocket.websocketDataBundle import \
        WebsocketDataBundle
except:
    import utils
    from backgroundTaskHelper import BackgroundTaskHelper
    from timber.timberInterface import TimberInterface

    from CynanBotCommon.twitch.websocket.twitchWebsocketClientInterface import \
        TwitchWebsocketClientInterface
    from twitch.websocket.twitchWebsocketClientListener import \
        TwitchWebsocketClientListener
    from twitch.websocket.websocketDataBundle import WebsocketDataBundle


class TwitchWebsocketClient(TwitchWebsocketClientInterface):

    def __init__(
        self,
        backgroundTaskHelper: BackgroundTaskHelper,
        timber: TimberInterface,
        twitchWebsocketUrl: str = 'wss://eventsub.wss.twitch.tv/ws'
    ):
        if not isinstance(backgroundTaskHelper, BackgroundTaskHelper):
            raise ValueError(f'backgroundTaskHelper argument is malformed: \"{backgroundTaskHelper}\"')
        elif not isinstance(timber, TimberInterface):
            raise ValueError(f'timber argument is malformed: \"{timber}\"')
        elif not utils.isValidUrl(twitchWebsocketUrl):
            raise ValueError(f'twitchWebsocketUrl argument is malformed: \"{twitchWebsocketUrl}\"')

        self.__backgroundTaskHelper: BackgroundTaskHelper = backgroundTaskHelper
        self.__timber: TimberInterface = timber
        self.__twitchWebsocketUrl: str = twitchWebsocketUrl

        self.__isStarted: bool = False
        self.__eventQueue: SimpleQueue[WebsocketDataBundle] = SimpleQueue()
        self.__listener: Optional[TwitchWebsocketClientListener] = None

    def setListener(self, listener: Optional[TwitchWebsocketClientListener]):
        if listener is not None and not isinstance(listener, TwitchWebsocketClientListener):
            raise ValueError(f'listener argument is malformed: \"{listener}\"')

        self.__listener = listener

    def start(self):
        if self.__isStarted:
            self.__timber.log('TwitchWebsocketClient', 'Not starting TwitchWebsocketClient as it has already been started')
            return

        self.__isStarted = True
        self.__timber.log('TwitchWebsocketClient', 'Starting TwitchWebsocketClient...')

        # TODO

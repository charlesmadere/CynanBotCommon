import asyncio
import queue
import traceback
from queue import SimpleQueue
from typing import Any, List, Optional

import websockets

try:
    import CynanBotCommon.utils as utils
    from CynanBotCommon.backgroundTaskHelper import BackgroundTaskHelper
    from CynanBotCommon.timber.timberInterface import TimberInterface
    from CynanBotCommon.twitch.websocket.twitchWebsocketClientInterface import \
        TwitchWebsocketClientInterface
    from CynanBotCommon.twitch.websocket.twitchWebsocketClientListener import \
        TwitchWebsocketClientListener
    from CynanBotCommon.twitch.websocket.twitchWebsocketJsonMapperInterface import \
        TwitchWebsocketJsonMapperInterface
    from CynanBotCommon.twitch.websocket.websocketDataBundle import \
        WebsocketDataBundle
except:
    import utils
    from backgroundTaskHelper import BackgroundTaskHelper
    from timber.timberInterface import TimberInterface

    from twitch.websocket.twitchWebsocketClientInterface import \
        TwitchWebsocketClientInterface
    from twitch.websocket.twitchWebsocketClientListener import \
        TwitchWebsocketClientListener
    from twitch.websocket.twitchWebsocketJsonMapperInterface import \
        TwitchWebsocketJsonMapperInterface
    from twitch.websocket.websocketDataBundle import WebsocketDataBundle


class TwitchWebsocketClient(TwitchWebsocketClientInterface):

    def __init__(
        self,
        backgroundTaskHelper: BackgroundTaskHelper,
        timber: TimberInterface,
        twitchWebsocketJsonMapper: TwitchWebsocketJsonMapperInterface,
        queueSleepTimeSeconds: float = 1,
        queueTimeoutSeconds: int = 3,
        sleepTimeSeconds: float = 3,
        twitchWebsocketUrl: str = 'wss://eventsub.wss.twitch.tv/ws'
    ):
        if not isinstance(backgroundTaskHelper, BackgroundTaskHelper):
            raise ValueError(f'backgroundTaskHelper argument is malformed: \"{backgroundTaskHelper}\"')
        elif not isinstance(timber, TimberInterface):
            raise ValueError(f'timber argument is malformed: \"{timber}\"')
        elif not isinstance(twitchWebsocketJsonMapper, TwitchWebsocketClientInterface):
            raise ValueError(f'twitchWebsocketJsonMapper argument is malformed: \"{twitchWebsocketJsonMapper}\"')
        elif not utils.isValidNum(queueSleepTimeSeconds):
            raise ValueError(f'queueSleepTimeSeconds argument is malformed: \"{queueSleepTimeSeconds}\"')
        elif queueSleepTimeSeconds < 1 or queueSleepTimeSeconds > 15:
            raise ValueError(f'queueSleepTimeSeconds argument is out of bounds: {queueSleepTimeSeconds}')
        elif not utils.isValidNum(queueTimeoutSeconds):
            raise ValueError(f'queueTimeoutSeconds argument is malformed: \"{queueTimeoutSeconds}\"')
        elif queueTimeoutSeconds < 1 or queueTimeoutSeconds > 5:
            raise ValueError(f'queueTimeoutSeconds argument is out of bounds: {queueTimeoutSeconds}')
        elif not utils.isValidNum(sleepTimeSeconds):
            raise ValueError(f'sleepTimeSeconds argument is malformed: \"{sleepTimeSeconds}\"')
        elif sleepTimeSeconds < 3 or sleepTimeSeconds > 10:
            raise ValueError(f'sleepTimeSeconds argument is out of bounds: {sleepTimeSeconds}')
        elif not utils.isValidUrl(twitchWebsocketUrl):
            raise ValueError(f'twitchWebsocketUrl argument is malformed: \"{twitchWebsocketUrl}\"')

        self.__backgroundTaskHelper: BackgroundTaskHelper = backgroundTaskHelper
        self.__timber: TimberInterface = timber
        self.__twitchWebsocketJsonMapper: TwitchWebsocketJsonMapperInterface = twitchWebsocketJsonMapper
        self.__queueSleepTimeSeconds: float = queueSleepTimeSeconds
        self.__queueTimeoutSeconds: int = queueTimeoutSeconds
        self.__sleepTimeSeconds: float = sleepTimeSeconds
        self.__twitchWebsocketUrl: str = twitchWebsocketUrl

        self.__isStarted: bool = False
        self.__eventQueue: SimpleQueue[WebsocketDataBundle] = SimpleQueue()
        self.__eventListener: Optional[TwitchWebsocketClientListener] = None

    async def __processMessage(self, message: Optional[Any]):
        if message is None:
            self.__timber.log('TwitchWebsocketClient', f'Received message object that is None: \"{message}\"')
            return
        if not isinstance(message, str):
            self.__timber.log('TwitchWebsocketClient', f'Received message object that is of an unexpected type: \"{message}\"')
            return

        dataBundle = await self.__twitchWebsocketJsonMapper.toWebsocketDataBundle(message)

        if dataBundle is None:
            self.__timber.log('TwitchWebsocketClient', f'Received message string that failed to be parsed: \"{message}\"')
            return

        await self.__submitEvent(dataBundle)

    def setEventListener(self, listener: Optional[TwitchWebsocketClientListener]):
        if listener is not None and not isinstance(listener, TwitchWebsocketClientListener):
            raise ValueError(f'listener argument is malformed: \"{listener}\"')

        self.__eventListener = listener

    def start(self):
        if self.__isStarted:
            self.__timber.log('TwitchWebsocketClient', 'Not starting TwitchWebsocketClient as it has already been started')
            return

        self.__isStarted = True
        self.__timber.log('TwitchWebsocketClient', 'Starting TwitchWebsocketClient...')

        self.__backgroundTaskHelper.createTask(self.__startWebsocketConnection())
        self.__backgroundTaskHelper.createTask(self.__startEventLoop())

    async def __startEventLoop(self):
        while True:
            eventListener = self.__eventListener

            if eventListener is not None:
                dataBundles: List[WebsocketDataBundle] = list()

                try:
                    while not self.__eventQueue.empty():
                        dataBundles.append(self.__eventQueue.get_nowait())
                except queue.Empty as e:
                    self.__timber.log('TwitchWebsocketClient', f'Encountered queue.Empty when building up dataBundles list (queue size: {self.__eventQueue.qsize()}) (dataBundles size: {len(dataBundles)})', e, traceback.format_exc())

                for dataBundle in dataBundles:
                    try:
                        await eventListener.onTwitchWebsocketClientEvent(dataBundle)
                    except Exception as e:
                        self.__timber.log('RecurringActionsMachine', f'Encountered unknown Exception when looping through events (queue size: {self.__eventQueue.qsize()}) (dataBundle: {dataBundle})', e, traceback.format_exc())

            await asyncio.sleep(self.__queueSleepTimeSeconds)

    async def __startWebsocketConnection(self):
        while True:
            try:
                async with websockets.connect(self.__twitchWebsocketUrl) as websocket:
                    try:
                        async for message in websocket:
                            await self.__processMessage(message)
                    except Exception as e:
                        self.__timber.log('TwitchWebsocketClient', f'Encountered exception when processing websocket message: {message}', e, traceback.format_exc())
            except Exception as e:
                self.__timber.log('TwitchWebsocketClient', f'Encountered websocket exception', e, traceback.format_exc())

            await asyncio.sleep(self.__sleepTimeSeconds)

    async def __submitEvent(self, dataBundle: WebsocketDataBundle):
        if not isinstance(dataBundle, WebsocketDataBundle):
            raise ValueError(f'event argument is malformed: \"{dataBundle}\"')

        try:
            self.__eventQueue.put(dataBundle, block = True, timeout = self.__queueTimeoutSeconds)
        except queue.Full as e:
            self.__timber.log('TwitchWebsocketClient', f'Encountered queue.Full when submitting a new event ({dataBundle}) into the event queue (queue size: {self.__eventQueue.qsize()})', e, traceback.format_exc())

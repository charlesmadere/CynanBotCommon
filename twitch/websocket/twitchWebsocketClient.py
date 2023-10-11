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
    from CynanBotCommon.twitch.websocket.twitchWebsocketDataBundleListener import \
        TwitchWebsocketDataBundleListener
    from CynanBotCommon.twitch.websocket.twitchWebsocketJsonMapperInterface import \
        TwitchWebsocketJsonMapperInterface
    from CynanBotCommon.twitch.websocket.websocketDataBundle import \
        WebsocketDataBundle
except:
    import utils
    from backgroundTaskHelper import BackgroundTaskHelper
    from timber.timberInterface import TimberInterface

    from CynanBotCommon.twitch.websocket.twitchWebsocketDataBundleListener import \
        TwitchWebsocketDataBundleListener
    from twitch.websocket.twitchWebsocketClientInterface import \
        TwitchWebsocketClientInterface
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
        websocketSleepTimeSeconds: float = 3,
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
        elif not utils.isValidNum(websocketSleepTimeSeconds):
            raise ValueError(f'websocketSleepTimeSeconds argument is malformed: \"{websocketSleepTimeSeconds}\"')
        elif websocketSleepTimeSeconds < 3 or websocketSleepTimeSeconds > 10:
            raise ValueError(f'websocketSleepTimeSeconds argument is out of bounds: {websocketSleepTimeSeconds}')
        elif not utils.isValidUrl(twitchWebsocketUrl):
            raise ValueError(f'twitchWebsocketUrl argument is malformed: \"{twitchWebsocketUrl}\"')

        self.__backgroundTaskHelper: BackgroundTaskHelper = backgroundTaskHelper
        self.__timber: TimberInterface = timber
        self.__twitchWebsocketJsonMapper: TwitchWebsocketJsonMapperInterface = twitchWebsocketJsonMapper
        self.__queueSleepTimeSeconds: float = queueSleepTimeSeconds
        self.__queueTimeoutSeconds: int = queueTimeoutSeconds
        self.__websocketSleepTimeSeconds: float = websocketSleepTimeSeconds
        self.__twitchWebsocketUrl: str = twitchWebsocketUrl

        self.__isStarted: bool = False
        self.__dataBundleQueue: SimpleQueue[WebsocketDataBundle] = SimpleQueue()
        self.__dataBundleListener: Optional[TwitchWebsocketDataBundleListener] = None

    async def __parseMessageToDataBundle(self, message: Optional[Any]) -> Optional[WebsocketDataBundle]:
        if message is None:
            self.__timber.log('TwitchWebsocketClient', f'Received message object that is None: \"{message}\"')
            return None
        elif not isinstance(message, str):
            self.__timber.log('TwitchWebsocketClient', f'Received message object that is of an unexpected type: \"{message}\"')
            return None
        else:
            return await self.__twitchWebsocketJsonMapper.toWebsocketDataBundle(message)

    def setDataBundleListener(self, listener: Optional[TwitchWebsocketDataBundleListener]):
        if listener is not None and not isinstance(listener, TwitchWebsocketDataBundleListener):
            raise ValueError(f'listener argument is malformed: \"{listener}\"')

        self.__dataBundleListener = listener

    def start(self):
        if self.__isStarted:
            self.__timber.log('TwitchWebsocketClient', 'Not starting TwitchWebsocketClient as it has already been started')
            return

        self.__isStarted = True
        self.__timber.log('TwitchWebsocketClient', 'Starting TwitchWebsocketClient...')

        self.__backgroundTaskHelper.createTask(self.__startWebsocketConnection())
        self.__backgroundTaskHelper.createTask(self.__startDataBundleLoop())

    async def __startDataBundleLoop(self):
        while True:
            dataBundleListener = self.__dataBundleListener

            if dataBundleListener is not None:
                dataBundles: List[WebsocketDataBundle] = list()

                try:
                    while not self.__dataBundleQueue.empty():
                        dataBundles.append(self.__dataBundleQueue.get_nowait())
                except queue.Empty as e:
                    self.__timber.log('TwitchWebsocketClient', f'Encountered queue.Empty when building up dataBundles list (queue size: {self.__dataBundleQueue.qsize()}) (dataBundles size: {len(dataBundles)})', e, traceback.format_exc())

                for dataBundle in dataBundles:
                    try:
                        await dataBundleListener.onNewWebsocketDataBundle(dataBundle)
                    except Exception as e:
                        self.__timber.log('RecurringActionsMachine', f'Encountered unknown Exception when looping through dataBundles (queue size: {self.__dataBundleQueue.qsize()}) (dataBundle: {dataBundle})', e, traceback.format_exc())

            await asyncio.sleep(self.__queueSleepTimeSeconds)

    async def __startWebsocketConnection(self):
        while True:
            try:
                self.__timber.log('TwitchWebsocketClient', f'Connecting to websocket \"{self.__twitchWebsocketUrl}\"...')

                async with websockets.connect(self.__twitchWebsocketUrl) as websocket:
                    async for message in websocket:
                        try:
                            dataBundle = await self.__parseMessageToDataBundle(message)

                            if dataBundle is None:
                                self.__timber.log('TwitchWebsocketClient', f'Websocket message was did not parse: \"{message}\"')
                            else:
                                await self.__submitDataBundle(dataBundle)
                        except Exception as e:
                            self.__timber.log('TwitchWebsocketClient', f'Encountered exception when parsing websocket message: {message}', e, traceback.format_exc())
            except Exception as e:
                self.__timber.log('TwitchWebsocketClient', f'Encountered websocket exception', e, traceback.format_exc())

            await asyncio.sleep(self.__websocketSleepTimeSeconds)

    async def __submitDataBundle(self, dataBundle: WebsocketDataBundle):
        if not isinstance(dataBundle, WebsocketDataBundle):
            raise ValueError(f'dataBundle argument is malformed: \"{dataBundle}\"')

        try:
            self.__dataBundleQueue.put(dataBundle, block = True, timeout = self.__queueTimeoutSeconds)
        except queue.Full as e:
            self.__timber.log('TwitchWebsocketClient', f'Encountered queue.Full when submitting a new dataBundle ({dataBundle}) into the dataBundle queue (queue size: {self.__dataBundleQueue.qsize()})', e, traceback.format_exc())

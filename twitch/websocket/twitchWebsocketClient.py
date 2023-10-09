import asyncio
import queue
import traceback
from queue import SimpleQueue
from typing import List, Optional

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
        queueSleepTimeSeconds: float = 1,
        queueTimeoutSeconds: int = 3,
        twitchWebsocketUrl: str = 'wss://eventsub.wss.twitch.tv/ws'
    ):
        if not isinstance(backgroundTaskHelper, BackgroundTaskHelper):
            raise ValueError(f'backgroundTaskHelper argument is malformed: \"{backgroundTaskHelper}\"')
        elif not isinstance(timber, TimberInterface):
            raise ValueError(f'timber argument is malformed: \"{timber}\"')
        elif not utils.isValidNum(queueSleepTimeSeconds):
            raise ValueError(f'queueSleepTimeSeconds argument is malformed: \"{queueSleepTimeSeconds}\"')
        elif queueSleepTimeSeconds < 1 or queueSleepTimeSeconds > 15:
            raise ValueError(f'queueSleepTimeSeconds argument is out of bounds: {queueSleepTimeSeconds}')
        elif not utils.isValidNum(queueTimeoutSeconds):
            raise ValueError(f'queueTimeoutSeconds argument is malformed: \"{queueTimeoutSeconds}\"')
        elif queueTimeoutSeconds < 1 or queueTimeoutSeconds > 5:
            raise ValueError(f'queueTimeoutSeconds argument is out of bounds: {queueTimeoutSeconds}')
        elif not utils.isValidUrl(twitchWebsocketUrl):
            raise ValueError(f'twitchWebsocketUrl argument is malformed: \"{twitchWebsocketUrl}\"')

        self.__backgroundTaskHelper: BackgroundTaskHelper = backgroundTaskHelper
        self.__timber: TimberInterface = timber
        self.__queueSleepTimeSeconds: float = queueSleepTimeSeconds
        self.__queueTimeoutSeconds: int = queueTimeoutSeconds
        self.__twitchWebsocketUrl: str = twitchWebsocketUrl

        self.__isStarted: bool = False
        self.__eventQueue: SimpleQueue[WebsocketDataBundle] = SimpleQueue()
        self.__eventListener: Optional[TwitchWebsocketClientListener] = None

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

    async def __submitEvent(self, event: WebsocketDataBundle):
        if not isinstance(event, WebsocketDataBundle):
            raise ValueError(f'event argument is malformed: \"{event}\"')

        try:
            self.__eventQueue.put(event, block = True, timeout = self.__queueTimeoutSeconds)
        except queue.Full as e:
            self.__timber.log('TwitchWebsocketClient', f'Encountered queue.Full when submitting a new event ({event}) into the event queue (queue size: {self.__eventQueue.qsize()})', e, traceback.format_exc())

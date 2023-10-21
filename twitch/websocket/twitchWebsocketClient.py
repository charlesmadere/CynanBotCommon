import asyncio
import queue
import traceback
from datetime import datetime, timedelta, timezone
from queue import SimpleQueue
from typing import Any, List, Optional

import websockets

try:
    import CynanBotCommon.utils as utils
    from CynanBotCommon.backgroundTaskHelper import BackgroundTaskHelper
    from CynanBotCommon.incrementalJsonBuilder import IncrementalJsonBuilder
    from CynanBotCommon.lruCache import LruCache
    from CynanBotCommon.timber.timberInterface import TimberInterface
    from CynanBotCommon.twitch.twitchApiServiceInterface import \
        TwitchApiServiceInterface
    from CynanBotCommon.twitch.twitchEventSubRequest import \
        TwitchEventSubRequest
    from CynanBotCommon.twitch.websocket.twitchWebsocketAllowedUsersRepositoryInterface import \
        TwitchWebsocketAllowedUsersRepositoryInterface
    from CynanBotCommon.twitch.websocket.twitchWebsocketClientInterface import \
        TwitchWebsocketClientInterface
    from CynanBotCommon.twitch.websocket.twitchWebsocketDataBundleListener import \
        TwitchWebsocketDataBundleListener
    from CynanBotCommon.twitch.websocket.twitchWebsocketJsonMapperInterface import \
        TwitchWebsocketJsonMapperInterface
    from CynanBotCommon.twitch.websocket.twitchWebsocketUser import \
        TwitchWebsocketUser
    from CynanBotCommon.twitch.websocket.websocketCondition import \
        WebsocketCondition
    from CynanBotCommon.twitch.websocket.websocketConnectionStatus import \
        WebsocketConnectionStatus
    from CynanBotCommon.twitch.websocket.websocketDataBundle import \
        WebsocketDataBundle
    from CynanBotCommon.twitch.websocket.websocketSubscriptionType import \
        WebsocketSubscriptionType
    from CynanBotCommon.twitch.websocket.websocketTransport import \
        WebsocketTransport
    from CynanBotCommon.twitch.websocket.websocketTransportMethod import \
        WebsocketTransportMethod
except:
    import utils
    from backgroundTaskHelper import BackgroundTaskHelper
    from incrementalJsonBuilder import IncrementalJsonBuilder
    from lruCache import LruCache
    from timber.timberInterface import TimberInterface

    from twitch.twitchApiServiceInterface import TwitchApiServiceInterface
    from twitch.twitchEventSubRequest import TwitchEventSubRequest
    from twitch.websocket.twitchWebsocketAllowedUsersRepositoryInterface import \
        TwitchWebsocketAllowedUsersRepositoryInterface
    from twitch.websocket.twitchWebsocketClientInterface import \
        TwitchWebsocketClientInterface
    from twitch.websocket.twitchWebsocketDataBundleListener import \
        TwitchWebsocketDataBundleListener
    from twitch.websocket.twitchWebsocketJsonMapperInterface import \
        TwitchWebsocketJsonMapperInterface
    from twitch.websocket.twitchWebsocketUser import TwitchWebsocketUser
    from twitch.websocket.websocketCondition import WebsocketCondition
    from twitch.websocket.websocketConnectionStatus import \
        WebsocketConnectionStatus
    from twitch.websocket.websocketDataBundle import WebsocketDataBundle
    from twitch.websocket.websocketSubscriptionType import \
        WebsocketSubscriptionType
    from twitch.websocket.websocketTransport import WebsocketTransport
    from twitch.websocket.websocketTransportMethod import \
        WebsocketTransportMethod


class TwitchWebsocketClient(TwitchWebsocketClientInterface):

    def __init__(
        self,
        backgroundTaskHelper: BackgroundTaskHelper,
        timber: TimberInterface,
        twitchApiService: TwitchApiServiceInterface,
        twitchWebsocketAllowedUsersRepository: TwitchWebsocketAllowedUsersRepositoryInterface,
        twitchWebsocketJsonMapper: TwitchWebsocketJsonMapperInterface,
        queueSleepTimeSeconds: float = 1,
        websocketSleepTimeSeconds: float = 3,
        queueTimeoutSeconds: int = 3,
        twitchWebsocketUrl: str = 'wss://eventsub.wss.twitch.tv/ws',
        maxMessageAge: timedelta = timedelta(minutes = 10),
        timeZone: timezone = timezone.utc
    ):
        if not isinstance(backgroundTaskHelper, BackgroundTaskHelper):
            raise ValueError(f'backgroundTaskHelper argument is malformed: \"{backgroundTaskHelper}\"')
        elif not isinstance(timber, TimberInterface):
            raise ValueError(f'timber argument is malformed: \"{timber}\"')
        elif not isinstance(twitchApiService, TwitchApiServiceInterface):
            raise ValueError(f'twitchApiService argument is malformed: \"{twitchApiService}\"')
        elif not isinstance(twitchWebsocketAllowedUsersRepository, TwitchWebsocketAllowedUsersRepositoryInterface):
            raise ValueError(f'twitchWebsocketAllowedUsersRepository argument is malformed: \"{twitchWebsocketAllowedUsersRepository}\"')
        elif not isinstance(twitchWebsocketJsonMapper, TwitchWebsocketJsonMapperInterface):
            raise ValueError(f'twitchWebsocketJsonMapper argument is malformed: \"{twitchWebsocketJsonMapper}\"')
        elif not utils.isValidNum(queueSleepTimeSeconds):
            raise ValueError(f'queueSleepTimeSeconds argument is malformed: \"{queueSleepTimeSeconds}\"')
        elif queueSleepTimeSeconds < 1 or queueSleepTimeSeconds > 15:
            raise ValueError(f'queueSleepTimeSeconds argument is out of bounds: {queueSleepTimeSeconds}')
        elif not utils.isValidNum(websocketSleepTimeSeconds):
            raise ValueError(f'websocketSleepTimeSeconds argument is malformed: \"{websocketSleepTimeSeconds}\"')
        elif websocketSleepTimeSeconds < 3 or websocketSleepTimeSeconds > 10:
            raise ValueError(f'websocketSleepTimeSeconds argument is out of bounds: {websocketSleepTimeSeconds}')
        elif not utils.isValidNum(queueTimeoutSeconds):
            raise ValueError(f'queueTimeoutSeconds argument is malformed: \"{queueTimeoutSeconds}\"')
        elif queueTimeoutSeconds < 1 or queueTimeoutSeconds > 5:
            raise ValueError(f'queueTimeoutSeconds argument is out of bounds: {queueTimeoutSeconds}')
        elif not utils.isValidUrl(twitchWebsocketUrl):
            raise ValueError(f'twitchWebsocketUrl argument is malformed: \"{twitchWebsocketUrl}\"')
        elif not isinstance(maxMessageAge, timedelta):
            raise ValueError(f'maxMessageAge argument is malformed: \"{maxMessageAge}\"')
        elif not isinstance(timeZone, timezone):
            raise ValueError(f'timeZone argument is malformed: \"{timeZone}\"')

        self.__backgroundTaskHelper: BackgroundTaskHelper = backgroundTaskHelper
        self.__timber: TimberInterface = timber
        self.__twitchApiService: TwitchApiServiceInterface = twitchApiService
        self.__twitchWebsocketAllowedUsersRepository: TwitchWebsocketAllowedUsersRepositoryInterface = twitchWebsocketAllowedUsersRepository
        self.__twitchWebsocketJsonMapper: TwitchWebsocketJsonMapperInterface = twitchWebsocketJsonMapper
        self.__queueSleepTimeSeconds: float = queueSleepTimeSeconds
        self.__websocketSleepTimeSeconds: float = websocketSleepTimeSeconds
        self.__queueTimeoutSeconds: int = queueTimeoutSeconds
        self.__twitchWebsocketUrl: str = twitchWebsocketUrl
        self.__maxMessageAge: timedelta = maxMessageAge
        self.__timeZone: timezone = timeZone

        self.__eventSubSubscriptionsCreated: bool = True
        self.__isStarted: bool = False
        self.__jsonBuilder: IncrementalJsonBuilder = IncrementalJsonBuilder()
        self.__messageIdCache: LruCache = LruCache(128)
        self.__dataBundleQueue: SimpleQueue[WebsocketDataBundle] = SimpleQueue()
        self.__sessionId: Optional[str] = None
        self.__dataBundleListener: Optional[TwitchWebsocketDataBundleListener] = None

    async def __cleanUpConnectionData(self):
        self.__sessionId = None
        self.__eventSubSubscriptionsCreated = False

    async def __createEventSubSubscription(self, sessionId: str, user: TwitchWebsocketUser):
        if not utils.isValidStr(sessionId):
            raise ValueError(f'sessionId argument is malformed: \"{sessionId}\"')
        elif not isinstance(user, TwitchWebsocketUser):
            raise ValueError(f'user argument is malformed: \"{user}\"')

        # this is the set of currently supported subscription types
        subscriptionTypes = { WebsocketSubscriptionType.CHANNEL_POINTS_REDEMPTION,
            WebsocketSubscriptionType.CHEER, WebsocketSubscriptionType.SUBSCRIBE, \
            WebsocketSubscriptionType.SUBSCRIPTION_GIFT, WebsocketSubscriptionType.SUBSCRIPTION_MESSAGE }

        transport = WebsocketTransport(
            sessionId = sessionId,
            method = WebsocketTransportMethod.WEBSOCKET
        )

        for index, subscriptionType in enumerate(subscriptionTypes):
            condition = await self.__createWebsocketCondition(
                user = user,
                subscriptionType = subscriptionType
            )

            eventSubRequest = TwitchEventSubRequest(
                condition = condition,
                subscriptionType = subscriptionType,
                transport = transport
            )

            response = await self.__twitchApiService.createEventSubSubscription(
                twitchAccessToken = user.getTwitchAccessToken(),
                eventSubRequest = eventSubRequest
            )

            self.__timber.log('TwitchWebsocketClient', f'Created EventSub subscription #{(index + 1)} for {user.getUserName()} (\"{subscriptionType}\"): {response}')

    async def __createEventSubSubscriptionsIfNecessary(self):
        if self.__eventSubSubscriptionsCreated:
            return

        sessionId = self.__sessionId

        if not utils.isValidStr(sessionId):
            return

        self.__eventSubSubscriptionsCreated = True
        users = await self.__twitchWebsocketAllowedUsersRepository.getUsers()
        self.__timber.log('TwitchWebsocketClient', f'Creating EventSub subscription(s) for {len(users)} user(s)...')

        for user in users:
            await self.__createEventSubSubscription(
                sessionId = sessionId,
                user = user
            )

        self.__timber.log('TwitchWebsocketClient', f'Finished creating EventSub subscription(s) for {len(users)}')

    async def __createWebsocketCondition(
        self,
        user: TwitchWebsocketUser,
        subscriptionType: WebsocketSubscriptionType
    ) -> WebsocketCondition:
        if not isinstance(user, TwitchWebsocketUser):
            raise ValueError(f'user argument is malformed: \"{user}\"')
        elif not isinstance(subscriptionType, WebsocketSubscriptionType):
            raise ValueError(f'subscriptionType argument is malformed: \"{subscriptionType}\"')

        if subscriptionType is WebsocketSubscriptionType.CHANNEL_POINTS_REDEMPTION:
            return WebsocketCondition(
                broadcasterUserId = user.getUserId()
            )
        elif subscriptionType is WebsocketSubscriptionType.CHEER:
            return WebsocketCondition(
                broadcasterUserId = user.getUserId()
            )
        elif subscriptionType is WebsocketSubscriptionType.FOLLOW:
            return WebsocketCondition(
                broadcasterUserId = user.getUserId(),
                moderatorUserId = user.getUserId()
            )
        elif subscriptionType is WebsocketSubscriptionType.RAID:
            return WebsocketCondition(
                toBroadcasterUserId = user.getUserId()
            )
        elif subscriptionType is WebsocketSubscriptionType.SUBSCRIBE or \
                subscriptionType is WebsocketSubscriptionType.SUBSCRIPTION_GIFT or \
                subscriptionType is WebsocketSubscriptionType.SUBSCRIPTION_MESSAGE:
            return WebsocketCondition(
                broadcasterUserId = user.getUserId()
            )
        else:
            raise RuntimeError(f'can\'t create a WebsocketCondition for the given unsupported WebsocketSubscriptionType: \"{subscriptionType}\"')

    async def __handleConnectionRelatedMessage(self, dataBundle: WebsocketDataBundle):
        if not isinstance(dataBundle, WebsocketDataBundle):
            raise ValueError(f'dataBundle argument is malformed: \"{dataBundle}\"')

        payload = dataBundle.getPayload()

        if payload is None:
            return

        session = payload.getSession()

        if session is None:
            return

        self.__timber.log('TwitchWebsocketClient', f'Session ID is being changed to \"{session.getSessionId()}\" from \"{self.__sessionId}\"')
        self.__sessionId = session.getSessionId()

    async def __isMessageConnectionRelated(self, dataBundle: WebsocketDataBundle) -> bool:
        if not isinstance(dataBundle, WebsocketDataBundle):
            raise ValueError(f'dataBundle argument is malformed: \"{dataBundle}\"')

        payload = dataBundle.getPayload()

        if payload is None:
            return True

        session = payload.getSession()

        if session is not None:
            self.__timber.log('TwitchWebsocketClient', f'Encountered a message that contains session data: \"{session}\"')
            return True
        else:
            return False

    async def __isValidMessage(self, dataBundle: WebsocketDataBundle) -> bool:
        if not isinstance(dataBundle, WebsocketDataBundle):
            raise ValueError(f'dataBundle argument is malformed: \"{dataBundle}\"')

        # ensure that this isn't a message we've seen before
        if self.__messageIdCache.contains(dataBundle.getMetadata().getMessageId()):
            self.__timber.log('TwitchWebsocketClient', f'Encountered a message ID that has already been seen: \"{dataBundle.getMetadata().getMessageId()}\"')
            return False

        self.__messageIdCache.put(dataBundle.getMetadata().getMessageId())

        # ensure that this message isn't gratuitously old
        messageTimestamp = dataBundle.getMetadata().getMessageTimestamp().getDateTime()
        now = datetime.now(self.__timeZone)

        if now - messageTimestamp >= self.__maxMessageAge:
            self.__timber.log('TwitchWebsocketClient', f'Encountered a message that is too old: \"{dataBundle.getMetadata().getMessageId()}\"')
            return False

        return True

    async def __parseMessageToDataBundles(self, message: Optional[Any]) -> Optional[List[WebsocketDataBundle]]:
        if message is None:
            self.__timber.log('TwitchWebsocketClient', f'Received message object that is None: \"{message}\"')
            return None
        elif not isinstance(message, str):
            self.__timber.log('TwitchWebsocketClient', f'Received message object that is of an unexpected type: \"{message}\"')
            return None

        dictionaries = await self.__jsonBuilder.buildDictionariesOrAppendInternalJsonCache(message)

        if not utils.hasItems(dictionaries):
            return None

        dataBundles: List[WebsocketDataBundle] = list()

        for index, dictionary in enumerate(dictionaries):
            dataBundle: Optional[WebsocketDataBundle] = None
            exception: Optional[Exception] = None

            try:
                dataBundle = await self.__twitchWebsocketJsonMapper.parseWebsocketDataBundle(dictionary)
            except Exception as e:
                exception = e

            if exception is not None:
                self.__timber.log('TwitchWebsocketClient', f'Encountered an exception when attempting to convert dictionary ({dictionary}) at index {index} into WebsocketDataBundle: {exception}', exception, traceback.format_exc())
                continue
            elif dataBundle is None:
                self.__timber.log('TwitchWebsocketClient', f'Received `None` when attempting to convert dictionary at index {index} into WebsocketDataBundle: \"{dictionary}\"')
                continue

            dataBundles.append(dataBundle)

        if utils.hasItems(dataBundles):
            return dataBundles
        else:
            return None

    async def __processDataBundles(self, dataBundles: List[WebsocketDataBundle]):
        if not utils.hasItems(dataBundles):
            raise ValueError(f'dataBundles argument is malformed: \"{dataBundles}\"')

        for dataBundle in dataBundles:
            if await self.__isMessageConnectionRelated(dataBundle):
                await self.__handleConnectionRelatedMessage(dataBundle)
                await self.__createEventSubSubscriptionsIfNecessary()
            else:
                await self.__submitDataBundle(dataBundle)

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
                    if not await self.__isValidMessage(dataBundle):
                        continue

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
                        dataBundles = await self.__parseMessageToDataBundles(message)

                        if not utils.hasItems(dataBundles):
                            continue

                        await self.__processDataBundles(dataBundles)
            except Exception as e:
                self.__timber.log('TwitchWebsocketClient', f'Encountered websocket exception', e, traceback.format_exc())
                await self.__cleanUpConnectionData()

            await asyncio.sleep(self.__websocketSleepTimeSeconds)

    async def __submitDataBundle(self, dataBundle: WebsocketDataBundle):
        if not isinstance(dataBundle, WebsocketDataBundle):
            raise ValueError(f'dataBundle argument is malformed: \"{dataBundle}\"')

        try:
            self.__dataBundleQueue.put(dataBundle, block = True, timeout = self.__queueTimeoutSeconds)
        except queue.Full as e:
            self.__timber.log('TwitchWebsocketClient', f'Encountered queue.Full when submitting a new dataBundle ({dataBundle}) into the dataBundle queue (queue size: {self.__dataBundleQueue.qsize()})', e, traceback.format_exc())

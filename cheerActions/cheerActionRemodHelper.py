import asyncio
import traceback
from typing import Optional

try:
    import CynanBotCommon.utils as utils
    from CynanBotCommon.backgroundTaskHelper import BackgroundTaskHelper
    from CynanBotCommon.cheerActions.cheerActionRemodData import \
        CheerActionRemodData
    from CynanBotCommon.cheerActions.cheerActionRemodHelperInterface import \
        CheerActionRemodHelperInterface
    from CynanBotCommon.timber.timberInterface import TimberInterface
    from CynanBotCommon.twitch.twitchApiServiceInterface import \
        TwitchApiServiceInterface
except:
    import utils
    from backgroundTaskHelper import BackgroundTaskHelper
    from cheerActions.cheerActionRemodData import CheerActionRemodData
    from timber.timberInterface import TimberInterface

    from CynanBotCommon.cheerActions.cheerActionRemodHelperInterface import \
        CheerActionRemodHelperInterface
    from twitch.twitchApiServiceInterface import TwitchApiServiceInterface


class CheerActionRemodHelper(CheerActionRemodHelperInterface):

    def __init__(
        self,
        backgroundTaskHelper: BackgroundTaskHelper,
        timber: TimberInterface,
        twitchApiService: TwitchApiServiceInterface,
        queueSleepTimeSeconds: float = 3,
        queueTimeoutSeconds: float = 3
    ):
        if not isinstance(backgroundTaskHelper, BackgroundTaskHelper):
            raise ValueError(f'backgroundTaskHelper argument is malformed: \"{backgroundTaskHelper}\"')
        elif not isinstance(timber, TimberInterface):
            raise ValueError(f'timber argument is malformed: \"{timber}\"')
        elif not isinstance(twitchApiService, TwitchApiServiceInterface):
            raise ValueError(f'twitchApiService argument is malformed: \"{twitchApiService}\"')
        elif not utils.isValidInt(queueSleepTimeSeconds):
            raise ValueError(f'queueSleepTimeSeconds argument is malformed: \"{queueSleepTimeSeconds}\"')
        elif queueSleepTimeSeconds < 1 or queueSleepTimeSeconds > 10:
            raise ValueError(f'queueSleepTimeSeconds argument is out of bounds: {queueSleepTimeSeconds}')
        elif not utils.isValidInt(queueTimeoutSeconds):
            raise ValueError(f'queueTimeoutSeconds argument is malformed: \"{queueTimeoutSeconds}\"')
        elif queueTimeoutSeconds < 1 or queueTimeoutSeconds > 3:
            raise ValueError(f'queueTimeoutSeconds argument is out of bounds: {queueTimeoutSeconds}')

        self.__backgroundTaskHelper: BackgroundTaskHelper = backgroundTaskHelper
        self.__timber: TimberInterface = timber
        self.__twitchApiService: TwitchApiServiceInterface = twitchApiService
        self.__queueSleepTimeSeconds: float = queueSleepTimeSeconds
        self.__queueTimeoutSeconds: float = queueTimeoutSeconds

        self.__isStarted: bool = False

    async def clearCaches(self):
        # TODO
        self.__timber.log('CheerActionRemodHelper', f'Caches cleared')

    def start(self):
        if self.__isStarted:
            self.__timber.log('CheerActionRemodHelper', 'Not starting CheerActionRemodHelper as it has already been started')
            return

        self.__isStarted = True
        self.__timber.log('CheerActionRemodHelper', 'Starting CheerActionRemodHelper...')

        self.__backgroundTaskHelper.createTask(self.__startEventLoop())

    async def __startEventLoop(self):
        while True:
            # TODO
            pass

            await asyncio.sleep(self.__queueSleepTimeSeconds)

    def submitRemodAction(action: CheerActionRemodData):
        if not isinstance(action, CheerActionRemodData):
            raise ValueError(f'action argument is malformed: \"{action}\"')

        # TODO
        pass

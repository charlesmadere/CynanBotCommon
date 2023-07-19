import asyncio
import queue
import random
import traceback
from datetime import datetime, timedelta, timezone
from queue import SimpleQueue
from typing import List, Optional

try:
    import CynanBotCommon.utils as utils
    from CynanBotCommon.backgroundTaskHelper import BackgroundTaskHelper
    from CynanBotCommon.recurringActions.mostRecentRecurringActionRepositoryInterface import \
        MostRecentRecurringActionRepositoryInterface
    from CynanBotCommon.recurringActions.recurringAction import RecurringAction
    from CynanBotCommon.recurringActions.recurringActionListener import \
        RecurringActionListener
    from CynanBotCommon.recurringActions.recurringActionsMachineInterface import \
        RecurringActionsMachineInterface
    from CynanBotCommon.recurringActions.recurringActionsRepositoryInterface import \
        RecurringActionsRepositoryInterface
    from CynanBotCommon.recurringActions.recurringActionType import \
        RecurringActionType
    from CynanBotCommon.timber.timberInterface import TimberInterface
    from CynanBotCommon.users.userInterface import UserInterface
    from CynanBotCommon.users.usersRepositoryInterface import \
        UsersRepositoryInterface
except:
    import utils
    from backgroundTaskHelper import BackgroundTaskHelper
    from recurringActions.mostRecentRecurringActionRepositoryInterface import \
        MostRecentRecurringActionRepositoryInterface
    from recurringActions.recurringAction import RecurringAction
    from recurringActions.recurringActionListener import \
        RecurringActionListener
    from recurringActions.recurringActionsMachineInterface import \
        RecurringActionsMachineInterface
    from recurringActions.recurringActionsRepositoryInterface import \
        RecurringActionsRepositoryInterface
    from recurringActions.recurringActionType import RecurringActionType
    from timber.timberInterface import TimberInterface

    from users.userInterface import UserInterface
    from users.usersRepositoryInterface import UsersRepositoryInterface


class RecurringActionsMachine(RecurringActionsMachineInterface):

    def __init__(
        self,
        backgroundTaskHelper: BackgroundTaskHelper,
        mostRecentRecurringActionRepository: MostRecentRecurringActionRepositoryInterface,
        recurringActionsRepository: RecurringActionsRepositoryInterface,
        timber: TimberInterface,
        usersRepository: UsersRepositoryInterface,
        queueSleepTimeSeconds: float = 3,
        refreshSleepTimeSeconds: float = 30,
        queueTimeoutSeconds: int = 3,
        cooldown: timedelta = timedelta(minutes = 3),
        timeZone: timezone = timezone.utc
    ):
        if not isinstance(backgroundTaskHelper, BackgroundTaskHelper):
            raise ValueError(f'backgroundTaskHelper argument is malformed: \"{backgroundTaskHelper}\"')
        elif not isinstance(mostRecentRecurringActionRepository, MostRecentRecurringActionRepositoryInterface):
            raise ValueError(f'mostRecentRecurringActionRepository argument is malformed: \"{mostRecentRecurringActionRepository}\"')
        elif not isinstance(recurringActionsRepository, RecurringActionsRepositoryInterface):
            raise ValueError(f'recurringActionsRepository argument is malformed: \"{recurringActionsRepository}\"')
        elif not isinstance(timber, TimberInterface):
            raise ValueError(f'timber argument is malformed: \"{timber}\"')
        elif not isinstance(usersRepository, UsersRepositoryInterface):
            raise ValueError(f'usersRepository argument is malformed: \"{usersRepository}\"')
        elif not utils.isValidNum(queueSleepTimeSeconds):
            raise ValueError(f'queueSleepTimeSeconds argument is malformed: \"{queueSleepTimeSeconds}\"')
        elif queueSleepTimeSeconds < 1 or queueSleepTimeSeconds > 15:
            raise ValueError(f'queueSleepTimeSeconds argument is out of bounds: {queueSleepTimeSeconds}')
        elif not utils.isValidNum(refreshSleepTimeSeconds):
            raise ValueError(f'refreshSleepTimeSeconds argument is malformed: \"{refreshSleepTimeSeconds}\"')
        elif refreshSleepTimeSeconds < 30 or refreshSleepTimeSeconds > 600:
            raise ValueError(f'refreshSleepTimeSeconds argument is out of bounds: {refreshSleepTimeSeconds}')
        elif not utils.isValidNum(queueTimeoutSeconds):
            raise ValueError(f'queueTimeoutSeconds argument is malformed: \"{queueTimeoutSeconds}\"')
        elif queueTimeoutSeconds < 1 or queueTimeoutSeconds > 5:
            raise ValueError(f'queueTimeoutSeconds argument is out of bounds: {queueTimeoutSeconds}')
        elif not isinstance(cooldown, timedelta):
            raise ValueError(f'cooldown argument is malformed: \"{cooldown}\"')
        elif not isinstance(timeZone, timezone):
            raise ValueError(f'timeZone argument is malformed: \"{timeZone}\"')

        self.__backgroundTaskHelper: BackgroundTaskHelper = backgroundTaskHelper
        self.__mostRecentRecurringActionsRepository: MostRecentRecurringActionRepositoryInterface = mostRecentRecurringActionRepository
        self.__recurringActionsRepository: RecurringActionsRepositoryInterface = recurringActionsRepository
        self.__timber: TimberInterface = timber
        self.__usersRepository: UsersRepositoryInterface = usersRepository
        self.__queueSleepTimeSeconds: float = queueSleepTimeSeconds
        self.__refreshSleepTimeSeconds: float = refreshSleepTimeSeconds
        self.__queueTimeoutSeconds: int = queueTimeoutSeconds
        self.__cooldown: timedelta = cooldown
        self.__timeZone: timezone = timeZone

        self.__isStarted: bool = False
        self.__actionListener: Optional[RecurringActionListener] = None
        self.__actionQueue: SimpleQueue[RecurringAction] = SimpleQueue()

    async def __processRecurringActionFor(self, user: UserInterface):
        if not isinstance(user, UserInterface):
            raise ValueError(f'user argument is malformed: \"{user}\"')

        actionTypes: List[RecurringActionType] = list(RecurringActionType)
        action: Optional[RecurringAction] = None

        mostRecentAction = await self.__mostRecentRecurringActionsRepository.getMostRecentRecurringAction(user.getHandle())
        now = datetime.now(self.__timeZone)

        while len(actionTypes) >= 1 and action is None:
            actionType = random.choice(actionTypes)
            actionTypes.remove(actionType)

            if actionType is RecurringActionType.SUPER_TRIVIA:
                action = await self.__recurringActionsRepository.getSuperTriviaRecurringAction(user.getHandle())
            elif actionType is RecurringActionType.WEATHER:
                action = await self.__recurringActionsRepository.getWeatherRecurringAction(user.getHandle())
            elif actionType is RecurringActionType.WORD_OF_THE_DAY:
                action = await self.__recurringActionsRepository.getWordOfTheDayRecurringAction(user.getHandle())
            else:
                raise RuntimeError(f'Unknown RecurringActionType: \"{actionType}\"')

            if mostRecentAction is not None and now < mostRecentAction.getDateTime() + self.__cooldown:
                action = None

        if action is None:
            return

        # TODO
        pass

    async def __refresh(self):
        users = await self.__usersRepository.getUsersAsync()

        for user in users:
            if not user.isEnabled() or not user.areRecurringActionsEnabled():
                users.remove(user)

        if not utils.hasItems(users):
            return

        for user in users:
            await self.__processRecurringActionFor(user)

    def setRecurringActionListener(self, listener: Optional[RecurringActionListener]):
        if listener is not None and not isinstance(listener, RecurringActionListener):
            raise ValueError(f'listener argument is malformed: \"{listener}\"')

        self.__actionListener = listener

    async def __startQueueLoop(self):
        while True:
            actionListener = self.__actionListener

            if actionListener is not None:
                pass

            # TODO
            pass

            await asyncio.sleep(self.__queueSleepTimeSeconds)

    def startRecurringActions(self):
        if self.__isStarted:
            self.__timber.log('RecurringActionsMachine', 'Not starting RecurringActionsMachine as it has already been started')
            return

        self.__isStarted = True
        self.__timber.log('RecurringActionsMachine', 'Starting RecurringActionsMachine...')

        self.__backgroundTaskHelper.createTask(self.__startRefreshLoop())
        self.__backgroundTaskHelper.createTask(self.__startQueueLoop())

    async def __startRefreshLoop(self):
        while True:
            try:
                await self.__refresh()
            except Exception as e:
                self.__timber.log('RecurringActionsMachine', f'Encountered unknown Exception when refreshing: {e}', e, traceback.format_exc())

            await asyncio.sleep(self.__refreshSleepTimeSeconds)

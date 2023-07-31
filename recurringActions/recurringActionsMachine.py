import asyncio
import queue
import random
import traceback
from datetime import datetime, timedelta, timezone
from queue import SimpleQueue
from typing import Dict, List, Optional

try:
    import CynanBotCommon.utils as utils
    from CynanBotCommon.backgroundTaskHelper import BackgroundTaskHelper
    from CynanBotCommon.language.wordOfTheDayRepository import \
        WordOfTheDayRepository
    from CynanBotCommon.language.wordOfTheDayResponse import \
        WordOfTheDayResponse
    from CynanBotCommon.location.locationsRepository import LocationsRepository
    from CynanBotCommon.recurringActions.immutableSuperTriviaRecurringAction import \
        ImmutableSuperTriviaRecurringAction
    from CynanBotCommon.recurringActions.immutableWeatherRecurringAction import \
        ImmutableWeatherRecurringAction
    from CynanBotCommon.recurringActions.immutableWordOfTheDayRecurringAction import \
        ImmutableWordOfTheDayRecurringAction
    from CynanBotCommon.recurringActions.mostRecentRecurringActionRepositoryInterface import \
        MostRecentRecurringActionRepositoryInterface
    from CynanBotCommon.recurringActions.recurringAction import RecurringAction
    from CynanBotCommon.recurringActions.recurringActionEventListener import \
        RecurringActionEventListener
    from CynanBotCommon.recurringActions.recurringActionsMachineInterface import \
        RecurringActionsMachineInterface
    from CynanBotCommon.recurringActions.recurringActionsRepositoryInterface import \
        RecurringActionsRepositoryInterface
    from CynanBotCommon.recurringActions.recurringActionType import \
        RecurringActionType
    from CynanBotCommon.recurringActions.superTriviaRecurringAction import \
        SuperTriviaRecurringAction
    from CynanBotCommon.recurringActions.weatherRecurringAction import \
        WeatherRecurringAction
    from CynanBotCommon.recurringActions.wordOfTheDayRecurringAction import \
        WordOfTheDayRecurringAction
    from CynanBotCommon.timber.timberInterface import TimberInterface
    from CynanBotCommon.trivia.triviaGameBuilderInterface import \
        TriviaGameBuilderInterface
    from CynanBotCommon.trivia.triviaGameMachine import TriviaGameMachine
    from CynanBotCommon.twitch.isLiveOnTwitchRepositoryInterface import \
        IsLiveOnTwitchRepositoryInterface
    from CynanBotCommon.users.userInterface import UserInterface
    from CynanBotCommon.users.usersRepositoryInterface import \
        UsersRepositoryInterface
    from CynanBotCommon.weather.weatherReport import WeatherReport
    from CynanBotCommon.weather.weatherRepository import WeatherRepository
except:
    import utils
    from backgroundTaskHelper import BackgroundTaskHelper
    from language.wordOfTheDayRepository import WordOfTheDayRepository
    from language.wordOfTheDayResponse import WordOfTheDayResponse
    from location.locationsRepository import LocationsRepository
    from recurringActions.immutableSuperTriviaRecurringAction import \
        ImmutableSuperTriviaRecurringAction
    from recurringActions.immutableWeatherRecurringAction import \
        ImmutableWeatherRecurringAction
    from recurringActions.immutableWordOfTheDayRecurringAction import \
        ImmutableWordOfTheDayRecurringAction
    from recurringActions.mostRecentRecurringActionRepositoryInterface import \
        MostRecentRecurringActionRepositoryInterface
    from recurringActions.recurringAction import RecurringAction
    from recurringActions.recurringActionListener import \
        RecurringActionEventListener
    from recurringActions.recurringActionsMachineInterface import \
        RecurringActionsMachineInterface
    from recurringActions.recurringActionsRepositoryInterface import \
        RecurringActionsRepositoryInterface
    from recurringActions.recurringActionType import RecurringActionType
    from recurringActions.superTriviaRecurringAction import \
        SuperTriviaRecurringAction
    from recurringActions.weatherRecurringAction import WeatherRecurringAction
    from recurringActions.wordOfTheDayRecurringAction import \
        WordOfTheDayRecurringAction
    from timber.timberInterface import TimberInterface
    from trivia.triviaGameBuilderInterface import TriviaGameBuilderInterface
    from trivia.triviaGameMachine import TriviaGameMachine
    from weather.weatherReport import WeatherReport
    from weather.weatherRepository import WeatherRepository

    from twitch.isLiveOnTwitchRepositoryInterface import \
        IsLiveOnTwitchRepositoryInterface
    from users.userInterface import UserInterface
    from users.usersRepositoryInterface import UsersRepositoryInterface


class RecurringActionsMachine(RecurringActionsMachineInterface):

    def __init__(
        self,
        backgroundTaskHelper: BackgroundTaskHelper,
        isLiveOnTwitchRepository: IsLiveOnTwitchRepositoryInterface,
        locationsRepository: LocationsRepository,
        mostRecentRecurringActionRepository: MostRecentRecurringActionRepositoryInterface,
        recurringActionsRepository: RecurringActionsRepositoryInterface,
        timber: TimberInterface,
        triviaGameBuilder: TriviaGameBuilderInterface,
        triviaGameMachine: TriviaGameMachine,
        usersRepository: UsersRepositoryInterface,
        weatherRepository: WeatherRepository,
        wordOfTheDayRepository: WordOfTheDayRepository,
        queueSleepTimeSeconds: float = 3,
        refreshSleepTimeSeconds: float = 30,
        queueTimeoutSeconds: int = 3,
        cooldown: timedelta = timedelta(minutes = 3),
        timeZone: timezone = timezone.utc
    ):
        if not isinstance(backgroundTaskHelper, BackgroundTaskHelper):
            raise ValueError(f'backgroundTaskHelper argument is malformed: \"{backgroundTaskHelper}\"')
        elif not isinstance(isLiveOnTwitchRepository, IsLiveOnTwitchRepositoryInterface):
            raise ValueError(f'isLiveOnTwitchRepository argument is malformed: \"{isLiveOnTwitchRepository}\"')
        elif not isinstance(locationsRepository, LocationsRepository):
            raise ValueError(f'locationsRepository argument is malformed: \"{locationsRepository}\"')
        elif not isinstance(mostRecentRecurringActionRepository, MostRecentRecurringActionRepositoryInterface):
            raise ValueError(f'mostRecentRecurringActionRepository argument is malformed: \"{mostRecentRecurringActionRepository}\"')
        elif not isinstance(recurringActionsRepository, RecurringActionsRepositoryInterface):
            raise ValueError(f'recurringActionsRepository argument is malformed: \"{recurringActionsRepository}\"')
        elif not isinstance(timber, TimberInterface):
            raise ValueError(f'timber argument is malformed: \"{timber}\"')
        elif not isinstance(triviaGameBuilder, TriviaGameBuilderInterface):
            raise ValueError(f'triviaGameBuilder argument is malformed: \"{triviaGameBuilder}\"')
        elif not isinstance(triviaGameMachine, TriviaGameMachine):
            raise ValueError(f'triviaGameMachine argument is malformed: \"{triviaGameMachine}\"')
        elif not isinstance(usersRepository, UsersRepositoryInterface):
            raise ValueError(f'usersRepository argument is malformed: \"{usersRepository}\"')
        elif not isinstance(weatherRepository, WeatherRepository):
            raise ValueError(f'weatherRepository argument is malformed: \"{weatherRepository}\"')
        elif not isinstance(wordOfTheDayRepository, WordOfTheDayRepository):
            raise ValueError(f'wordOfTheDayRepository argument is malformed: \"{wordOfTheDayRepository}\"')
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
        self.__isLiveOnTwitchRepository: IsLiveOnTwitchRepositoryInterface = isLiveOnTwitchRepository
        self.__locationsRepository: LocationsRepository = locationsRepository
        self.__mostRecentRecurringActionsRepository: MostRecentRecurringActionRepositoryInterface = mostRecentRecurringActionRepository
        self.__recurringActionsRepository: RecurringActionsRepositoryInterface = recurringActionsRepository
        self.__timber: TimberInterface = timber
        self.__triviaGameBuilder: TriviaGameBuilderInterface = triviaGameBuilder
        self.__triviaGameMachine: TriviaGameMachine = triviaGameMachine
        self.__usersRepository: UsersRepositoryInterface = usersRepository
        self.__weatherRepository: WeatherRepository = weatherRepository
        self.__wordOfTheDayRepository: WordOfTheDayRepository = wordOfTheDayRepository
        self.__queueSleepTimeSeconds: float = queueSleepTimeSeconds
        self.__refreshSleepTimeSeconds: float = refreshSleepTimeSeconds
        self.__queueTimeoutSeconds: int = queueTimeoutSeconds
        self.__cooldown: timedelta = cooldown
        self.__timeZone: timezone = timeZone

        self.__isStarted: bool = False
        self.__eventListener: Optional[RecurringActionEventListener] = None
        self.__eventQueue: SimpleQueue[RecurringAction] = SimpleQueue()

    async def __findDueRecurringAction(self, user: UserInterface) -> Optional[RecurringAction]:
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

            if mostRecentAction is not None and action is not None:
                if now < mostRecentAction.getDateTime() + self.__cooldown:
                    action = None
                else:
                    minutesBetweenInt = action.getMinutesBetween()

                    if not utils.isValidInt(minutesBetweenInt):
                        minutesBetweenInt = action.getActionType().getDefaultRecurringActionTimingMinutes()

                    minutesBetween = timedelta(minutes = minutesBetweenInt)

                    if now < mostRecentAction.getDateTime() + minutesBetween:
                        action = None

        return action

    async def __processRecurringAction(self, user: UserInterface, action: RecurringAction):
        if not isinstance(user, UserInterface):
            raise ValueError(f'user argument is malformed: \"{user}\"')
        elif not isinstance(action, RecurringAction):
            raise ValueError(f'action argument is malformed: \"{action}\"')

        actionType = action.getActionType()

        if actionType is RecurringActionType.SUPER_TRIVIA:
            action = await self.__processSuperTriviaRecurringAction(
                user = user,
                action = action
            )
        elif actionType is RecurringActionType.WEATHER:
            action = await self.__processWeatherRecurringAction(
                user = user,
                action = action
            )
        elif actionType is RecurringActionType.WORD_OF_THE_DAY:
            action = await self.__processWordOfTheDayRecurringAction(
                user = user,
                action = action
            )
        else:
            raise RuntimeError(f'Unknown RecurringActionType: \"{actionType}\"')

    async def __processSuperTriviaRecurringAction(
        self,
        user: UserInterface,
        action: SuperTriviaRecurringAction
    ) -> bool:
        if not isinstance(user, UserInterface):
            raise ValueError(f'user argument is malformed: \"{user}\"')
        elif not isinstance(action, SuperTriviaRecurringAction):
            raise ValueError(f'action argument is malformed: \"{action}\"')

        newTriviaGame = await self.__triviaGameBuilder.createNewSuperTriviaGame(
            twitchChannel = user.getHandle(),
            numberOfGames = 1
        )

        if newTriviaGame is None:
            return False

        self.__triviaGameMachine.submitAction(newTriviaGame)

        await self.__submitEvent(ImmutableSuperTriviaRecurringAction(
            twitchChannel = action.getTwitchChannel(),
            enabled = action.isEnabled(),
            minutesBetween = action.getMinutesBetween()
        ))

        return True

    async def __processWeatherRecurringAction(
        self,
        user: UserInterface,
        action: WeatherRecurringAction
    ) -> bool:
        if not isinstance(user, UserInterface):
            raise ValueError(f'user argument is malformed: \"{user}\"')
        elif not isinstance(action, WeatherRecurringAction):
            raise ValueError(f'action argument is malformed: \"{action}\"')

        if not user.hasLocationId():
            return False

        location = await self.__locationsRepository.getLocation(user.getLocationId())
        weatherReport: Optional[WeatherReport] = None

        try:
            weatherReport = await self.__weatherRepository.fetchWeather(location)
        except:
            return False

        if weatherReport is None:
            return False
        elif action.isAlertsOnly() and not weatherReport.hasAlerts():
            return False

        await self.__submitEvent(ImmutableWeatherRecurringAction(
            twitchChannel = action.getTwitchChannel(),
            alertsOnly = action.isAlertsOnly(),
            enabled = action.isEnabled(),
            minutesBetween = action.getMinutesBetween(),
            weatherReport = weatherReport
        ))

        return True

    async def __processWordOfTheDayRecurringAction(
        self,
        user: UserInterface,
        action: WordOfTheDayRecurringAction
    ) -> bool:
        if not isinstance(user, UserInterface):
            raise ValueError(f'user argument is malformed: \"{user}\"')
        elif not isinstance(action, WordOfTheDayRecurringAction):
            raise ValueError(f'action argument is malformed: \"{action}\"')

        if not action.hasLanguageEntry():
            return False

        wordOfTheDayResponse = Optional[WordOfTheDayResponse] = None

        try:
            wordOfTheDayResponse = await self.__wordOfTheDayRepository.fetchWotd(action.requireLanguageEntry())
        except:
            return False

        if wordOfTheDayResponse is None:
            return False

        await self.__submitEvent(ImmutableWordOfTheDayRecurringAction(
            twitchChannel = action.getTwitchChannel(),
            enabled = action.isEnabled(),
            minutesBetween = action.getMinutesBetween(),
            languageEntry = action.getLanguageEntry(),
            wordOfTheDayResponse = wordOfTheDayResponse
        ))

        return True

    async def __refresh(self):
        users = await self.__usersRepository.getUsersAsync()
        usersToRemove: List[UserInterface] = list()

        for user in users:
            if not user.isEnabled() or not user.areRecurringActionsEnabled():
                usersToRemove.append(user)

        for userToRemove in usersToRemove:
            users.remove(userToRemove)

        if not utils.hasItems(users):
            return

        usersToRemove.clear()
        usersToRecurringAction: Dict[UserInterface, RecurringAction] = dict()

        for user in users:
            action = await self.__findDueRecurringAction(user)

            if action is not None:
                usersToRecurringAction[user] = action

        twitchHandles = list(usersToRecurringAction.keys())
        usersToLiveStatus = await self.__isLiveOnTwitchRepository.isLive(twitchHandles)

        for user, action in usersToRecurringAction.items():
            if not usersToLiveStatus.get(user.getHandle(), False):
                continue

            if await self.__processRecurringAction(
                user = user,
                action = action
            ):
                await self.__mostRecentRecurringActionsRepository.setMostRecentRecurringAction(action)

    def setRecurringActionListener(self, listener: Optional[RecurringActionEventListener]):
        if listener is not None and not isinstance(listener, RecurringActionEventListener):
            raise ValueError(f'listener argument is malformed: \"{listener}\"')

        self.__eventListener = listener

    async def __startEventLoop(self):
        while True:
            eventListener = self.__eventListener

            if eventListener is not None:
                events: List[RecurringAction] = list()
                pass

                try:
                    while not self.__eventQueue.empty():
                        events.append(self.__eventQueue.get_nowait())
                except queue.Empty as e:
                    self.__timber.log('RecurringActionsMachine', f'Encountered queue.Empty when building up events list (queue size: {self.__eventQueue.qsize()}) (events size: {len(events)})', e, traceback.format_exc())

            for event in events:
                try:
                    await eventListener.onNewRecurringActionEvent(event)
                except Exception as e:
                    self.__timber.log('RecurringActionsMachine', f'Encountered unknown Exception when looping through events (queue size: {self.__eventQueue.qsize()}) (event: {event})', e, traceback.format_exc())

            await asyncio.sleep(self.__queueSleepTimeSeconds)

    def startRecurringActions(self):
        if self.__isStarted:
            self.__timber.log('RecurringActionsMachine', 'Not starting RecurringActionsMachine as it has already been started')
            return

        self.__isStarted = True
        self.__timber.log('RecurringActionsMachine', 'Starting RecurringActionsMachine...')

        self.__backgroundTaskHelper.createTask(self.__startRefreshLoop())
        self.__backgroundTaskHelper.createTask(self.__startEventLoop())

    async def __startRefreshLoop(self):
        while True:
            try:
                await self.__refresh()
            except Exception as e:
                self.__timber.log('RecurringActionsMachine', f'Encountered unknown Exception when refreshing: {e}', e, traceback.format_exc())

            await asyncio.sleep(self.__refreshSleepTimeSeconds)

    async def __submitEvent(self, event: RecurringAction):
        if not isinstance(event, RecurringAction):
            raise ValueError(f'action argument is malformed: \"{event}\"')

        try:
            self.__eventQueue.put(event, block = True, timeout = self.__queueTimeoutSeconds)
        except queue.Full as e:
            self.__timber.log('RecurringActionsMachine', f'Encountered queue.Full when submitting a new event ({event}) into the event queue (queue size: {self.__eventQueue.qsize()})', e, traceback.format_exc())

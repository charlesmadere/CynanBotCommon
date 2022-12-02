import queue
from collections import defaultdict
from queue import SimpleQueue
from typing import Dict, List, Set

try:
    import CynanBotCommon.utils as utils
    from CynanBotCommon.timber.timber import Timber
    from CynanBotCommon.trivia.addQueuedGamesResult import AddQueuedGamesResult
    from CynanBotCommon.trivia.clearQueuedGamesResult import \
        ClearQueuedGamesResult
    from CynanBotCommon.trivia.startNewSuperTriviaGameAction import \
        StartNewSuperTriviaGameAction
    from CynanBotCommon.trivia.triviaSettingsRepository import \
        TriviaSettingsRepository
except:
    import utils
    from timber.timber import Timber
    from trivia.addQueuedGamesResult import AddQueuedGamesResult
    from trivia.clearQueuedGamesResult import ClearQueuedGamesResult
    from trivia.startNewSuperTriviaGameAction import \
        StartNewSuperTriviaGameAction
    from trivia.triviaSettingsRepository import TriviaSettingsRepository


class QueuedTriviaGameStore():

    def __init__(
        self,
        timber: Timber,
        triviaSettingsRepository: TriviaSettingsRepository,
        queueTimeoutSeconds: int = 3
    ):
        if timber is None:
            raise ValueError(f'timber argument is malformed: \"{timber}\"')
        elif triviaSettingsRepository is None:
            raise ValueError(f'triviaSettingsRepository argument is malformed: \"{triviaSettingsRepository}\"')
        elif not utils.isValidNum(queueTimeoutSeconds):
            raise ValueError(f'queueTimeoutSeconds argument is malformed: \"{queueTimeoutSeconds}\"')
        elif queueTimeoutSeconds < 1 or queueTimeoutSeconds > 5:
            raise ValueError(f'queueTimeoutSeconds argument is out of bounds: {queueTimeoutSeconds}')

        self.__timber: Timber = timber
        self.__triviaSettingsRepository: TriviaSettingsRepository = triviaSettingsRepository
        self.__queueTimeoutSeconds: int = queueTimeoutSeconds

        self.__queuedSuperGames: Dict[str, SimpleQueue[StartNewSuperTriviaGameAction]] = defaultdict(lambda: SimpleQueue())

    async def addSuperGames(
        self,
        isSuperTriviaGameCurrentlyInProgress: bool,
        action: StartNewSuperTriviaGameAction
    ) -> AddQueuedGamesResult:
        if not utils.isValidBool(isSuperTriviaGameCurrentlyInProgress):
            raise ValueError(f'isSuperTriviaGameCurrentlyInProgress argument is malformed: \"{isSuperTriviaGameCurrentlyInProgress}\"')
        elif action is None:
            raise ValueError(f'action argument is malformed: \"{action}\"')

        queuedSuperGames = self.__queuedSuperGames[action.getTwitchChannel().lower()]
        oldQueueSize = queuedSuperGames.qsize()

        if action.isQueueActionConsumed():
            return AddQueuedGamesResult(
                amountAdded = 0,
                newQueueSize = oldQueueSize,
                oldQueueSize = oldQueueSize
            )

        action.consumeQueueAction()
        maxSuperGameQueueSize = await self.__triviaSettingsRepository.getMaxSuperGameQueueSize()

        if maxSuperGameQueueSize < 1:
            return AddQueuedGamesResult(
                amountAdded = 0,
                newQueueSize = oldQueueSize,
                oldQueueSize = oldQueueSize
            )

        numberOfGames = action.getNumberOfGames()

        if not isSuperTriviaGameCurrentlyInProgress:
            numberOfGames = numberOfGames - 1

            if numberOfGames < 1:
                return AddQueuedGamesResult(
                    amountAdded = 0,
                    newQueueSize = oldQueueSize,
                    oldQueueSize = oldQueueSize
                )

        amountAdded: int = 0

        for _ in range(numberOfGames):
            if queuedSuperGames.qsize() < maxSuperGameQueueSize:
                queuedSuperGames.put(StartNewSuperTriviaGameAction(
                    isQueueActionConsumed = True,
                    numberOfGames = 1,
                    perUserAttempts = action.getPerUserAttempts(),
                    pointsForWinning = action.getPointsForWinning(),
                    pointsMultiplier = action.getPointsMultiplier(),
                    secondsToLive = action.getSecondsToLive(),
                    twitchChannel = action.getTwitchChannel(),
                    triviaFetchOptions = action.getTriviaFetchOptions()
                ))
                amountAdded = amountAdded + 1
            else:
                break

        return AddQueuedGamesResult(
            amountAdded = amountAdded,
            newQueueSize = queuedSuperGames.qsize(),
            oldQueueSize = oldQueueSize
        )

    async def clearQueuedSuperTriviaGames(self, twitchChannel: str) -> ClearQueuedGamesResult:
        if not utils.isValidStr(twitchChannel):
            raise ValueError(f'twitchChannel argument is malformed: \"{twitchChannel}\"')

        queuedSuperGames = self.__queuedSuperGames[twitchChannel.lower()]
        oldQueueSize = queuedSuperGames.qsize()
        amountRemoved: int = 0

        try:
            while not queuedSuperGames.empty():
                queuedSuperGames.get(block = True, timeout = self.__queueTimeoutSeconds)
                amountRemoved = amountRemoved + 1
        except queue.Empty as e:
            self.__timber.log('QueuedTriviaGameStore', f'Unable to clear all queued super games for \"{twitchChannel}\" (queue size: {queuedSuperGames.qsize()}) (oldQueueSize: {oldQueueSize}): {e}', e)

        self.__timber.log('QueuedTriviaGameStore', f'Cleared {amountRemoved} super games for \"{twitchChannel}\" (oldQueueSize: {oldQueueSize})')

        return ClearQueuedGamesResult(
            amountRemoved = amountRemoved,
            oldQueueSize = oldQueueSize
        )

    async def getQueuedSuperGamesSize(self, twitchChannel: str) -> int:
        if not utils.isValidStr(twitchChannel):
            raise ValueError(f'twitchChannel argument is malformed: \"{twitchChannel}\"')

        twitchChannel = twitchChannel.lower()
        return self.__queuedSuperGames[twitchChannel].qsize()

    async def popQueuedSuperGames(self, activeChannels: List[str]) -> List[StartNewSuperTriviaGameAction]:
        workingActiveChannels: Set[str] = set()
        for activeChannel in activeChannels:
            workingActiveChannels.add(activeChannel.lower())

        superGames: List[StartNewSuperTriviaGameAction] = list()

        for twitchChannel, queuedSuperGames in self.__queuedSuperGames.items():
            if twitchChannel.lower() in workingActiveChannels:
                continue
            elif queuedSuperGames.empty():
                continue

            try:
                superGames.append(queuedSuperGames.get(block = True, timeout = self.__queueTimeoutSeconds))
            except queue.Empty as e:
                self.__timber.log('QueuedTriviaGameStore', f'Unable to get queued super game for \"{twitchChannel}\" (queue size: {queuedSuperGames.qsize()}): {e}', e)

        return superGames

import queue
from collections import defaultdict
from queue import SimpleQueue
from typing import Dict, List, Set

try:
    import CynanBotCommon.utils as utils
    from CynanBotCommon.timber.timberInterface import TimberInterface
    from CynanBotCommon.trivia.addQueuedGamesResult import AddQueuedGamesResult
    from CynanBotCommon.trivia.clearQueuedGamesResult import \
        ClearQueuedGamesResult
    from CynanBotCommon.trivia.queuedTriviaGameStoreInterface import \
        QueuedTriviaGameStoreInterface
    from CynanBotCommon.trivia.startNewSuperTriviaGameAction import \
        StartNewSuperTriviaGameAction
    from CynanBotCommon.trivia.triviaSettingsRepositoryInterface import \
        TriviaSettingsRepositoryInterface
except:
    import utils
    from timber.timberInterface import TimberInterface
    from trivia.addQueuedGamesResult import AddQueuedGamesResult
    from trivia.clearQueuedGamesResult import ClearQueuedGamesResult
    from trivia.queuedTriviaGameStoreInterface import \
        QueuedTriviaGameStoreInterface
    from trivia.startNewSuperTriviaGameAction import \
        StartNewSuperTriviaGameAction
    from trivia.triviaSettingsRepositoryInterface import \
        TriviaSettingsRepositoryInterface


class QueuedTriviaGameStore(QueuedTriviaGameStoreInterface):

    def __init__(
        self,
        timber: TimberInterface,
        triviaSettingsRepository: TriviaSettingsRepositoryInterface,
        queueTimeoutSeconds: int = 3
    ):
        if not isinstance(timber, TimberInterface):
            raise ValueError(f'timber argument is malformed: \"{timber}\"')
        elif not isinstance(triviaSettingsRepository, TriviaSettingsRepositoryInterface):
            raise ValueError(f'triviaSettingsRepository argument is malformed: \"{triviaSettingsRepository}\"')
        elif not utils.isValidNum(queueTimeoutSeconds):
            raise ValueError(f'queueTimeoutSeconds argument is malformed: \"{queueTimeoutSeconds}\"')
        elif queueTimeoutSeconds < 1 or queueTimeoutSeconds > 5:
            raise ValueError(f'queueTimeoutSeconds argument is out of bounds: {queueTimeoutSeconds}')

        self.__timber: TimberInterface = timber
        self.__triviaSettingsRepository: TriviaSettingsRepositoryInterface = triviaSettingsRepository
        self.__queueTimeoutSeconds: int = queueTimeoutSeconds

        self.__queuedSuperGames: Dict[str, SimpleQueue[StartNewSuperTriviaGameAction]] = defaultdict(lambda: SimpleQueue())

    async def addSuperGames(
        self,
        isSuperTriviaGameCurrentlyInProgress: bool,
        action: StartNewSuperTriviaGameAction
    ) -> AddQueuedGamesResult:
        if not utils.isValidBool(isSuperTriviaGameCurrentlyInProgress):
            raise ValueError(f'isSuperTriviaGameCurrentlyInProgress argument is malformed: \"{isSuperTriviaGameCurrentlyInProgress}\"')
        elif not isinstance(action, StartNewSuperTriviaGameAction):
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
        maxSuperTriviaGameQueueSize = await self.__triviaSettingsRepository.getMaxSuperTriviaGameQueueSize()

        if maxSuperTriviaGameQueueSize < 1:
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
            if queuedSuperGames.qsize() < maxSuperTriviaGameQueueSize:
                queuedSuperGames.put(StartNewSuperTriviaGameAction(
                    isQueueActionConsumed = True,
                    isShinyTriviaEnabled = action.isShinyTriviaEnabled(),
                    isToxicTriviaEnabled = action.isToxicTriviaEnabled(),
                    numberOfGames = 1,
                    perUserAttempts = action.getPerUserAttempts(),
                    pointsForWinning = action.getPointsForWinning(),
                    regularTriviaPointsForWinning = action.getRegularTriviaPointsForWinning(),
                    secondsToLive = action.getSecondsToLive(),
                    shinyMultiplier = action.getShinyMultiplier(),
                    toxicMultiplier = action.getToxicMultiplier(),
                    toxicTriviaPunishmentMultiplier = action.getToxicTriviaPunishmentMultiplier(),
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

    async def clearQueuedSuperGames(self, twitchChannel: str) -> ClearQueuedGamesResult:
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

        return ClearQueuedGamesResult(
            amountRemoved = amountRemoved,
            oldQueueSize = oldQueueSize
        )

    async def getQueuedSuperGamesSize(self, twitchChannel: str) -> int:
        if not utils.isValidStr(twitchChannel):
            raise ValueError(f'twitchChannel argument is malformed: \"{twitchChannel}\"')

        twitchChannel = twitchChannel.lower()

        if twitchChannel in self.__queuedSuperGames:
            return self.__queuedSuperGames[twitchChannel].qsize()
        else:
            return 0

    async def popQueuedSuperGames(self, activeChannels: Set[str]) -> List[StartNewSuperTriviaGameAction]:
        superGames: List[StartNewSuperTriviaGameAction] = list()

        for twitchChannel, queuedSuperGames in self.__queuedSuperGames.items():
            if twitchChannel.lower() in activeChannels:
                continue
            elif queuedSuperGames.empty():
                continue

            try:
                superGames.append(queuedSuperGames.get(block = True, timeout = self.__queueTimeoutSeconds))
            except queue.Empty as e:
                self.__timber.log('QueuedTriviaGameStore', f'Unable to get queued super game for \"{twitchChannel}\" (queue size: {queuedSuperGames.qsize()}): {e}', e)

        return superGames

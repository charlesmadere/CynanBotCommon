import locale

try:
    import CynanBotCommon.utils as utils
    from CynanBotCommon.trivia.absTriviaAction import AbsTriviaAction
    from CynanBotCommon.trivia.triviaActionType import TriviaActionType
    from CynanBotCommon.trivia.triviaFetchOptions import TriviaFetchOptions
except:
    import utils
    from trivia.absTriviaAction import AbsTriviaAction
    from trivia.triviaActionType import TriviaActionType
    from trivia.triviaFetchOptions import TriviaFetchOptions


class StartNewSuperTriviaGameAction(AbsTriviaAction):

    def __init__(
        self,
        isQueueActionConsumed: bool,
        numberOfGames: int,
        perUserAttempts: int,
        pointsForWinning: int,
        pointsMultiplier: int,
        secondsToLive: int,
        twitchChannel: str,
        triviaFetchOptions: TriviaFetchOptions
    ):
        super().__init__(triviaActionType = TriviaActionType.START_NEW_SUPER_GAME)

        if not utils.isValidBool(isQueueActionConsumed):
            raise ValueError(f'isQueueActionConsumed argument is malformed: \"{isQueueActionConsumed}\"')
        elif not utils.isValidInt(numberOfGames):
            raise ValueError(f'numberOfGames argument is malformed: \"{numberOfGames}\"')
        elif numberOfGames < 1 or numberOfGames >= utils.getIntMaxSafeSize():
            raise ValueError(f'numberOfGames argument is out of bounds: {numberOfGames}')
        elif not utils.isValidInt(perUserAttempts):
            raise ValueError(f'perUserAttempts argument is malformed: \"{perUserAttempts}\"')
        elif perUserAttempts < 1 or perUserAttempts > 5:
            raise ValueError(f'perUserAttempts argument is out of bounds: {perUserAttempts}')
        elif not utils.isValidInt(pointsForWinning):
            raise ValueError(f'pointsForWinning argument is malformed: \"{pointsForWinning}\"')
        elif pointsForWinning < 1 or pointsForWinning >= utils.getIntMaxSafeSize():
            raise ValueError(f'pointsForWinning argument is out of bounds: {pointsForWinning}')
        elif not utils.isValidInt(pointsMultiplier):
            raise ValueError(f'pointsMultiplier argument is malformed: \"{pointsMultiplier}\"')
        elif pointsMultiplier < 1 or pointsForWinning >= utils.getIntMaxSafeSize():
            raise ValueError(f'pointsMultiplier argument is out of bounds: {pointsMultiplier}')
        elif not utils.isValidInt(secondsToLive):
            raise ValueError(f'secondsToLive argument is malformed: \"{secondsToLive}\"')
        elif secondsToLive < 1 or secondsToLive >= utils.getIntMaxSafeSize():
            raise ValueError(f'secondsToLive argument is out of bounds: {secondsToLive}')
        elif not utils.isValidStr(twitchChannel):
            raise ValueError(f'twitchChannel argument is malformed: \"{twitchChannel}\"')
        elif not isinstance(triviaFetchOptions, TriviaFetchOptions):
            raise ValueError(f'triviaFetchOptions argument is malformed: \"{triviaFetchOptions}\"')

        self.__isQueueActionConsumed: bool = isQueueActionConsumed
        self.__numberOfGames: int = numberOfGames
        self.__perUserAttempts: int = perUserAttempts
        self.__pointsForWinning: int = pointsForWinning
        self.__pointsMultiplier: int = pointsMultiplier
        self.__secondsToLive: int = secondsToLive
        self.__twitchChannel: str = twitchChannel
        self.__triviaFetchOptions: TriviaFetchOptions = triviaFetchOptions

    def consumeQueueAction(self):
        self.__isQueueActionConsumed = True

    def getNumberOfGames(self) -> int:
        return self.__numberOfGames

    def getNumberOfGamesStr(self) -> str:
        return locale.format_string("%d", self.__numberOfGames, grouping = True)

    def getPerUserAttempts(self) -> int:
        return self.__perUserAttempts

    def getPointsForWinning(self) -> int:
        return self.__pointsForWinning

    def getPointsForWinningStr(self) -> str:
        return locale.format_string("%d", self.__pointsForWinning, grouping = True)

    def getPointsMultiplier(self) -> int:
        return self.__pointsMultiplier

    def getPointsMulitplierStr(self) -> str:
        return locale.format_string("%d", self.__pointsMultiplier, grouping = True)

    def getSecondsToLive(self) -> int:
        return self.__secondsToLive

    def getSecondsToLiveStr(self) -> str:
        return locale.format_string("%d", self.__secondsToLive, grouping = True)

    def getTriviaFetchOptions(self) -> TriviaFetchOptions:
        return self.__triviaFetchOptions

    def getTwitchChannel(self) -> str:
        return self.__twitchChannel

    def isQueueActionConsumed(self) -> bool:
        return self.__isQueueActionConsumed

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


class StartNewTriviaGameAction(AbsTriviaAction):

    def __init__(
        self,
        pointsForWinning: int,
        secondsToLive: int,
        twitchChannel: str,
        userId: str,
        userName: str,
        triviaFetchOptions: TriviaFetchOptions
    ):
        super().__init__(triviaActionType = TriviaActionType.START_NEW_GAME)

        if not utils.isValidNum(pointsForWinning):
            raise ValueError(f'pointsForWinning argument is malformed: \"{pointsForWinning}\"')
        elif pointsForWinning < 1:
            raise ValueError(f'pointsForWinning argument is out of bounds: {pointsForWinning}')
        elif not utils.isValidNum(secondsToLive):
            raise ValueError(f'secondsToLive argument is malformed: \"{secondsToLive}\"')
        elif secondsToLive < 1:
            raise ValueError(f'secondsToLive argument is out of bounds: {secondsToLive}')
        elif not utils.isValidStr(twitchChannel):
            raise ValueError(f'twitchChannel argument is malformed: \"{twitchChannel}\"')
        elif not utils.isValidStr(userId):
            raise ValueError(f'userId argument is malformed: \"{userId}\"')
        elif not utils.isValidStr(userName):
            raise ValueError(f'userName argument is malformed: \"{userName}\"')
        elif triviaFetchOptions is None:
            raise ValueError(f'triviaFetchOptions argument is malformed: \"{triviaFetchOptions}\"')

        self.__pointsForWinning: int = pointsForWinning
        self.__secondsToLive: int = secondsToLive
        self.__twitchChannel: str = twitchChannel
        self.__userId: str = userId
        self.__userName: str = userName
        self.__triviaFetchOptions: TriviaFetchOptions = triviaFetchOptions

    def getPointsForWinning(self) -> int:
        return self.__pointsForWinning

    def getPointsForWinningStr(self) -> str:
        return locale.format_string("%d", self.__pointsForWinning, grouping = True)

    def getSecondsToLive(self) -> int:
        return self.__secondsToLive

    def getSecondsToLiveStr(self) -> str:
        return locale.format_string("%d", self.__secondsToLive, grouping = True)

    def getTriviaFetchOptions(self) -> TriviaFetchOptions:
        return self.__triviaFetchOptions

    def getTwitchChannel(self) -> str:
        return self.__twitchChannel

    def getUserId(self) -> str:
        return self.__userId

    def getUserName(self) -> str:
        return self.__userName

import locale

try:
    import CynanBotCommon.utils as utils
    from CynanBotCommon.trivia.absTriviaEvent import AbsTriviaEvent
    from CynanBotCommon.trivia.absTriviaQuestion import AbsTriviaQuestion
    from CynanBotCommon.trivia.triviaEventType import TriviaEventType
except:
    import utils
    from trivia.absTriviaEvent import AbsTriviaEvent
    from trivia.absTriviaQuestion import AbsTriviaQuestion
    from trivia.triviaEventType import TriviaEventType


class NewTriviaGameEvent(AbsTriviaEvent):

    def __init__(
        self,
        triviaQuestion: AbsTriviaQuestion,
        isShiny: bool,
        pointsForWinning: int,
        secondsToLive: int,
        shinyTriviaMultiplier: int,
        actionId: str,
        gameId: str,
        twitchChannel: str,
        userId: str,
        userName: str
    ):
        super().__init__(
            actionId = actionId,
            triviaEventType = TriviaEventType.NEW_GAME
        )

        if not isinstance(triviaQuestion, AbsTriviaQuestion):
            raise ValueError(f'triviaQuestion argument is malformed: \"{triviaQuestion}\"')
        elif not utils.isValidBool(isShiny):
            raise ValueError(f'isShiny argument is malformed: \"{isShiny}\"')
        elif not utils.isValidInt(pointsForWinning):
            raise ValueError(f'pointsForWinning argument is malformed: \"{pointsForWinning}\"')
        elif pointsForWinning < 1 or pointsForWinning >= utils.getIntMaxSafeSize():
            raise ValueError(f'pointsForWinning argument is out of bounds: {pointsForWinning}')
        elif not utils.isValidInt(secondsToLive):
            raise ValueError(f'secondsToLive argument is malformed: \"{secondsToLive}\"')
        elif secondsToLive < 1 or secondsToLive >= utils.getIntMaxSafeSize():
            raise ValueError(f'secondsToLive argument is out of bounds: {secondsToLive}')
        elif not utils.isValidInt(shinyTriviaMultiplier):
            raise ValueError(f'shinyTriviaMultiplier argument is malformed: \"{shinyTriviaMultiplier}\"')
        elif shinyTriviaMultiplier < 1 or shinyTriviaMultiplier >= utils.getIntMaxSafeSize():
            raise ValueError(f'shinyTriviaMultiplier argument is out of bounds: {shinyTriviaMultiplier}')
        elif not utils.isValidStr(gameId):
            raise ValueError(f'gameId argument is malformed: \"{gameId}\"')
        elif not utils.isValidStr(twitchChannel):
            raise ValueError(f'twitchChannel argument is malformed: \"{twitchChannel}\"')
        elif not utils.isValidStr(userId):
            raise ValueError(f'userId argument is malformed: \"{userId}\"')
        elif not utils.isValidStr(userName):
            raise ValueError(f'userName argument is malformed: \"{userName}\"')

        self.__triviaQuestion: AbsTriviaQuestion = triviaQuestion
        self.__isShiny: bool = isShiny
        self.__pointsForWinning: int = pointsForWinning
        self.__secondsToLive: int = secondsToLive
        self.__shinyTriviaMultiplier: int = shinyTriviaMultiplier
        self.__gameId: str = gameId
        self.__twitchChannel: str = twitchChannel
        self.__userId: str = userId
        self.__userName: str = userName

    def getGameId(self) -> str:
        return self.__gameId

    def getPointsForWinning(self) -> int:
        return self.__pointsForWinning

    def getPointsForWinningStr(self) -> str:
        return locale.format_string("%d", self.__pointsForWinning, grouping = True)

    def getSecondsToLive(self) -> int:
        return self.__secondsToLive

    def getSecondsToLiveStr(self) -> str:
        return locale.format_string("%d", self.__secondsToLive, grouping = True)

    def getShinyTriviaMultiplier(self) -> int:
        return self.__shinyTriviaMultiplier

    def getShinyTriviaMultiplierStr(self) -> str:
        return locale.format_string("%d", self.__shinyTriviaMultiplier, grouping = True)

    def getTriviaQuestion(self) -> AbsTriviaQuestion:
        return self.__triviaQuestion

    def getTwitchChannel(self) -> str:
        return self.__twitchChannel

    def getUserId(self) -> str:
        return self.__userId

    def getUserName(self) -> str:
        return self.__userName

    def isShiny(self) -> bool:
        return self.__isShiny

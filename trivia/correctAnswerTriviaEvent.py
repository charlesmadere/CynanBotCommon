try:
    import CynanBotCommon.utils as utils
    from CynanBotCommon.trivia.absTriviaEvent import AbsTriviaEvent
    from CynanBotCommon.trivia.absTriviaQuestion import AbsTriviaQuestion
    from CynanBotCommon.trivia.triviaEventType import TriviaEventType
    from CynanBotCommon.trivia.triviaScoreResult import TriviaScoreResult
except:
    import utils

    from trivia.absTriviaEvent import AbsTriviaEvent
    from trivia.absTriviaQuestion import AbsTriviaQuestion
    from trivia.triviaEventType import TriviaEventType
    from trivia.triviaScoreResult import TriviaScoreResult


class CorrectAnswerTriviaEvent(AbsTriviaEvent):

    def __init__(
        self,
        triviaQuestion: AbsTriviaQuestion,
        pointsForWinning: int,
        answer: str,
        gameId: str,
        twitchChannel: str,
        userId: str,
        userName: str,
        triviaScoreResult: TriviaScoreResult
    ):
        super().__init__(triviaEventType = TriviaEventType.CORRECT_ANSWER)

        if triviaQuestion is None:
            raise ValueError(f'triviaQuestion argument is malformed: \"{triviaQuestion}\"')
        elif not utils.isValidNum(pointsForWinning):
            raise ValueError(f'pointsForWinning argument is malformed: \"{pointsForWinning}\"')
        elif pointsForWinning < 1:
            raise ValueError(f'pointsForWinning argument is out of bounds: {pointsForWinning}')
        elif not utils.isValidStr(gameId):
            raise ValueError(f'gameId argument is malformed: \"{gameId}\"')
        elif not utils.isValidStr(twitchChannel):
            raise ValueError(f'twitchChannel argument is malformed: \"{twitchChannel}\"')
        elif not utils.isValidStr(answer):
            raise ValueError(f'answer argument is malformed: \"{answer}\"')
        elif not utils.isValidStr(userId):
            raise ValueError(f'userId argument is malformed: \"{userId}\"')
        elif not utils.isValidStr(userName):
            raise ValueError(f'userName argument is malformed: \"{userName}\"')
        elif triviaScoreResult is None:
            raise ValueError(f'triviaScoreResult argument is malformed: \"{triviaScoreResult}\"')

        self.__triviaQuestion: AbsTriviaQuestion = triviaQuestion
        self.__pointsForWinning: int = pointsForWinning
        self.__answer: str = answer
        self.__gameId: str = gameId
        self.__twitchChannel: str = twitchChannel
        self.__userId: str = userId
        self.__userName: str = userName
        self.__triviaScoreResult: TriviaScoreResult = triviaScoreResult

    def getAnswer(self) -> str:
        return self.__answer

    def getGameId(self) -> str:
        return self.__gameId

    def getPointsForWinning(self) -> int:
        return self.__pointsForWinning

    def getTriviaQuestion(self) -> AbsTriviaQuestion:
        return self.__triviaQuestion

    def getTriviaScoreResult(self) -> TriviaScoreResult:
        return self.__triviaScoreResult

    def getTwitchChannel(self) -> str:
        return self.__twitchChannel

    def getUserId(self) -> str:
        return self.__userId

    def getUserName(self) -> str:
        return self.__userName

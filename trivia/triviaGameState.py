from datetime import datetime, timedelta, timezone

try:
    import CynanBotCommon.utils as utils
    from CynanBotCommon.trivia.absTriviaQuestion import AbsTriviaQuestion
except:
    import utils

    from trivia.absTriviaQuestion import AbsTriviaQuestion


class TriviaGameState():

    def __init__(
        self,
        triviaQuestion: AbsTriviaQuestion,
        pointsForWinning: int,
        secondsToLive: int,
        twitchChannel: str,
        userId: str,
        userName: str
    ):
        if triviaQuestion is None:
            raise ValueError(f'triviaQuestion argument is malformed: \"{triviaQuestion}\"')
        elif not utils.isValidNum(pointsForWinning):
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

        self.__triviaQuestion: AbsTriviaQuestion = triviaQuestion
        self.__pointsForWinning: int = pointsForWinning
        self.__secondsToLive: int = secondsToLive
        self.__twitchChannel: str = twitchChannel
        self.__userId: str = userId
        self.__userName: str = userName

        self.__endTime: datetime = datetime.now(timezone.utc) + timedelta(seconds = secondsToLive)

    def getEndTime(self) -> datetime:
        return self.__endTime

    def getPointsForWinning(self) -> int:
        return self.__pointsForWinning

    def getSecondsToLive(self) -> int:
        return self.__secondsToLive

    def getTriviaQuestion(self) -> AbsTriviaQuestion:
        return self.__triviaQuestion

    def getTwitchChannel(self) -> str:
        return self.__twitchChannel

    def getUserId(self) -> str:
        return self.__userId

    def getUserName(self) -> str:
        return self.__userName

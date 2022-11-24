import random
import string
from abc import ABC
from datetime import datetime, timedelta, timezone

try:
    import CynanBotCommon.utils as utils
    from CynanBotCommon.trivia.absTriviaQuestion import AbsTriviaQuestion
    from CynanBotCommon.trivia.triviaGameType import TriviaGameType
except:
    import utils
    from trivia.absTriviaQuestion import AbsTriviaQuestion
    from trivia.triviaGameType import TriviaGameType


class AbsTriviaGameState(ABC):

    def __init__(
        self,
        triviaQuestion: AbsTriviaQuestion,
        pointsForWinning: int,
        secondsToLive: int,
        actionId: str,
        twitchChannel: str,
        triviaGameType: TriviaGameType
    ):
        if triviaQuestion is None:
            raise ValueError(f'triviaQuestion argument is malformed: \"{triviaQuestion}\"')
        elif not utils.isValidNum(pointsForWinning):
            raise ValueError(f'pointsForWinning argument is malformed: \"{pointsForWinning}\"')
        elif pointsForWinning < 1:
            raise ValueError(f'pointsForWinning argument is out of bounds: {pointsForWinning}')
        elif not utils.isValidNum(secondsToLive):
            raise ValueError(f'secondsToLive argument is malformed: \"{secondsToLive}\"')
        elif secondsToLive < 1 or secondsToLive > utils.getIntMaxSafeSize():
            raise ValueError(f'secondsToLive argument is out of bounds: {secondsToLive}')
        elif not utils.isValidStr(actionId):
            raise ValueError(f'actionId argument is malformed: \"{actionId}\"')
        elif not utils.isValidStr(twitchChannel):
            raise ValueError(f'twitchChannel argument is malformed: \"{twitchChannel}\"')
        elif triviaGameType is None:
            raise ValueError(f'triviaGameType argument is malformed: \"{triviaGameType}\"')

        self.__triviaQuestion: AbsTriviaQuestion = triviaQuestion
        self.__pointsForWinning: int = pointsForWinning
        self.__secondsToLive: int = secondsToLive
        self.__actionId: str = actionId
        self.__twitchChannel: str = twitchChannel
        self.__triviaGameType: TriviaGameType = triviaGameType

        self.__endTime: datetime = datetime.now(timezone.utc) + timedelta(seconds = secondsToLive)
        self.__gameId: str = ''.join(random.choice(string.ascii_lowercase) for _ in range(12))

    def getActionId(self) -> str:
        return self.__actionId

    def getEndTime(self) -> datetime:
        return self.__endTime

    def getGameId(self) -> str:
        return self.__gameId

    def getPointsForWinning(self) -> int:
        return self.__pointsForWinning

    def getSecondsToLive(self) -> int:
        return self.__secondsToLive

    def getTriviaGameType(self) -> TriviaGameType:
        return self.__triviaGameType

    def getTriviaQuestion(self) -> AbsTriviaQuestion:
        return self.__triviaQuestion

    def getTwitchChannel(self) -> str:
        return self.__twitchChannel

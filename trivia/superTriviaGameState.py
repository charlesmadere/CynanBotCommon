from collections import defaultdict
from typing import Dict

try:
    import CynanBotCommon.utils as utils
    from CynanBotCommon.trivia.absTriviaGameState import AbsTriviaGameState
    from CynanBotCommon.trivia.absTriviaQuestion import AbsTriviaQuestion
    from CynanBotCommon.trivia.triviaGameType import TriviaGameType
except:
    import utils

    from trivia.absTriviaGameState import AbsTriviaGameState
    from trivia.absTriviaQuestion import AbsTriviaQuestion
    from trivia.triviaGameType import TriviaGameType


class SuperTriviaGameState(AbsTriviaGameState):

    def __init__(
        self,
        triviaQuestion: AbsTriviaQuestion,
        pointsForWinning: int,
        pointsMultiplier: int,
        secondsToLive: int,
        twitchChannel: str
    ):
        super().__init__(
            triviaQuestion = triviaQuestion,
            pointsForWinning = pointsForWinning,
            secondsToLive = secondsToLive,
            twitchChannel = twitchChannel,
            triviaGameType = TriviaGameType.SUPER
        )

        if not utils.isValidNum(pointsMultiplier):
            raise ValueError(f'pointsMultiplier argument is malformed: \"{pointsMultiplier}\"')
        elif pointsMultiplier < 1:
            raise ValueError(f'pointsMultiplier argument is out of bounds: {pointsMultiplier}')

        self.__pointsMultiplier: int = pointsMultiplier

        self.__answeredUserNames: Dict[str, bool] = defaultdict(lambda: False)

    def hasAnswered(self, userName: str) -> bool:
        if not utils.isValidStr(userName):
            raise ValueError(f'userName argument is malformed: \"{userName}\"')

        return self.__answeredUserNames[userName.lower()]

    def getPointsMultiplier(self) -> int:
        return self.__pointsMultiplier

    def setHasAnswered(self, userName: str):
        if not utils.isValidStr(userName):
            raise ValueError(f'userName argument is malformed: \"{userName}\"')

        self.__answeredUserNames[userName.lower()] = True

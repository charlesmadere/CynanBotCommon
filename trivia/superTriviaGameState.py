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
        isShiny: bool,
        perUserAttempts: int,
        pointsForWinning: int,
        secondsToLive: int,
        shinyMultiplier: int,
        actionId: str,
        twitchChannel: str
    ):
        super().__init__(
            triviaQuestion = triviaQuestion,
            isShiny = isShiny,
            pointsForWinning = pointsForWinning,
            secondsToLive = secondsToLive,
            shinyMultiplier = shinyMultiplier,
            actionId = actionId,
            twitchChannel = twitchChannel,
            triviaGameType = TriviaGameType.SUPER
        )

        if not utils.isValidInt(perUserAttempts):
            raise ValueError(f'perUserAttempts argument is malformed: \"{perUserAttempts}\"')
        elif perUserAttempts < 1 or perUserAttempts > 5:
            raise ValueError(f'perUserAttempts argument is out of bounds: {perUserAttempts}')

        self.__perUserAttempts: int = perUserAttempts

        self.__answeredUserIds: Dict[str, int] = defaultdict(lambda: 0)

    def getPerUserAttempts(self) -> int:
        return self.__perUserAttempts

    def incrementAnswerCount(self, userId: str):
        if not utils.isValidStr(userId):
            raise ValueError(f'userId argument is malformed: \"{userId}\"')

        userId = userId.lower()
        self.__answeredUserIds[userId] = self.__answeredUserIds[userId] + 1

    def isEligibleToAnswer(self, userId: str) -> bool:
        if not utils.isValidStr(userId):
            raise ValueError(f'userId argument is malformed: \"{userId}\"')

        userId = userId.lower()
        return self.__answeredUserIds[userId] < self.__perUserAttempts

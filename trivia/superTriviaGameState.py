from collections import defaultdict
from typing import Dict, Optional

try:
    import CynanBotCommon.utils as utils
    from CynanBotCommon.trivia.absTriviaGameState import AbsTriviaGameState
    from CynanBotCommon.trivia.absTriviaQuestion import AbsTriviaQuestion
    from CynanBotCommon.trivia.specialTriviaStatus import SpecialTriviaStatus
    from CynanBotCommon.trivia.triviaGameType import TriviaGameType
except:
    import utils
    from trivia.absTriviaGameState import AbsTriviaGameState
    from trivia.absTriviaQuestion import AbsTriviaQuestion
    from trivia.specialTriviaStatus import SpecialTriviaStatus
    from trivia.triviaGameType import TriviaGameType


class SuperTriviaGameState(AbsTriviaGameState):

    def __init__(
        self,
        triviaQuestion: AbsTriviaQuestion,
        perUserAttempts: int,
        pointsForWinning: int,
        secondsToLive: int,
        toxicTriviaPunishmentAmount: int,
        specialTriviaStatus: Optional[SpecialTriviaStatus],
        actionId: str,
        emote: str,
        twitchChannel: str
    ):
        super().__init__(
            triviaQuestion = triviaQuestion,
            pointsForWinning = pointsForWinning,
            secondsToLive = secondsToLive,
            specialTriviaStatus = specialTriviaStatus,
            actionId = actionId,
            emote = emote,
            twitchChannel = twitchChannel,
            triviaGameType = TriviaGameType.SUPER
        )

        if not utils.isValidInt(perUserAttempts):
            raise ValueError(f'perUserAttempts argument is malformed: \"{perUserAttempts}\"')
        elif perUserAttempts < 1 or perUserAttempts > 3:
            raise ValueError(f'perUserAttempts argument is out of bounds: {perUserAttempts}')
        elif not utils.isValidInt(toxicTriviaPunishmentAmount):
            raise ValueError(f'toxicTriviaPunishmentAmount argument is malformed: \"{toxicTriviaPunishmentAmount}\"')
        elif toxicTriviaPunishmentAmount < 0 or toxicTriviaPunishmentAmount > utils.getIntMaxSafeSize():
            raise ValueError(f'toxicTriviaPunishmentAmount argument is out of bounds: {toxicTriviaPunishmentAmount}')

        self.__perUserAttempts: int = perUserAttempts
        self.__toxicTriviaPunishmentAmount: int = toxicTriviaPunishmentAmount

        self.__answeredUserIds: Dict[str, int] = defaultdict(lambda: 0)

    def getAnsweredUserIds(self) -> Dict[str, int]:
        return dict(self.__answeredUserIds)

    def getPerUserAttempts(self) -> int:
        return self.__perUserAttempts

    def getToxicTriviaPunishmentAmount(self) -> int:
        return self.__toxicTriviaPunishmentAmount

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

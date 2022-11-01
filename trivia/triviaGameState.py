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


class TriviaGameState(AbsTriviaGameState):

    def __init__(
        self,
        triviaQuestion: AbsTriviaQuestion,
        pointsForWinning: int,
        secondsToLive: int,
        actionId: str,
        twitchChannel: str,
        userId: str,
        userName: str
    ):
        super().__init__(
            triviaQuestion = triviaQuestion,
            pointsForWinning = pointsForWinning,
            secondsToLive = secondsToLive,
            actionId = actionId,
            twitchChannel = twitchChannel,
            triviaGameType = TriviaGameType.NORMAL
        )

        if not utils.isValidStr(userId):
            raise ValueError(f'userId argument is malformed: \"{userId}\"')
        elif not utils.isValidStr(userName):
            raise ValueError(f'userName argument is malformed: \"{userName}\"')

        self.__userId: str = userId
        self.__userName: str = userName

    def getUserId(self) -> str:
        return self.__userId

    def getUserName(self) -> str:
        return self.__userName

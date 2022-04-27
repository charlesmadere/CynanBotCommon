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


class OutOfTimeSuperTriviaEvent(AbsTriviaEvent):

    def __init__(
        self,
        triviaQuestion: AbsTriviaQuestion,
        gameId: str,
        twitchChannel: str
    ):
        super().__init__(triviaEventType = TriviaEventType.SUPER_GAME_OUT_OF_TIME)

        if triviaQuestion is None:
            raise ValueError(f'triviaQuestion argument is malformed: \"{triviaQuestion}\"')
        elif not utils.isValidStr(gameId):
            raise ValueError(f'gameId argument is malformed: \"{gameId}\"')
        elif not utils.isValidStr(twitchChannel):
            raise ValueError(f'twitchChannel argument is malformed: \"{twitchChannel}\"')

        self.__triviaQuestion: AbsTriviaQuestion = triviaQuestion
        self.__gameId: str = gameId
        self.__twitchChannel: str = twitchChannel

    def getGameId(self) -> str:
        return self.__gameId

    def getTriviaQuestion(self) -> AbsTriviaQuestion:
        return self.__triviaQuestion

    def getTwitchChannel(self) -> str:
        return self.__twitchChannel

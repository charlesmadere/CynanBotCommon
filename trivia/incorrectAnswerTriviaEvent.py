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


class IncorrectAnswerTriviaEvent(AbsTriviaEvent):

    def __init__(
        self,
        triviaQuestion: AbsTriviaQuestion,
        answer: str,
        twitchChannel: str,
        userId: str,
        userName: str
    ):
        super().__init__(triviaEventType = TriviaEventType.INCORRECT_ANSWER)

        if triviaQuestion is None:
            raise ValueError(f'triviaQuestion argument is malformed: \"{triviaQuestion}\"')
        elif not utils.isValidStr(twitchChannel):
            raise ValueError(f'twitchChannel argument is malformed: \"{twitchChannel}\"')
        elif not utils.isValidStr(userId):
            raise ValueError(f'userId argument is malformed: \"{userId}\"')
        elif not utils.isValidStr(userName):
            raise ValueError(f'userName argument is malformed: \"{userName}\"')

        self.__triviaQuestion: AbsTriviaQuestion = triviaQuestion
        self.__answer: str = answer
        self.__twitchChannel: str = twitchChannel
        self.__userId: str = userId
        self.__userName: str = userName

    def getAnswer(self) -> str:
        return self.__answer

    def getTriviaQuestion(self) -> AbsTriviaQuestion:
        return self.__triviaQuestion

    def getTwitchChannel(self) -> str:
        return self.__twitchChannel

    def getUserId(self) -> str:
        return self.__userId

    def getUserName(self) -> str:
        return self.__userName
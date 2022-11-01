try:
    import CynanBotCommon.utils as utils
    from CynanBotCommon.trivia.absTriviaEvent import AbsTriviaEvent
    from CynanBotCommon.trivia.triviaEventType import TriviaEventType
except:
    import utils

    from trivia.absTriviaEvent import AbsTriviaEvent
    from trivia.triviaEventType import TriviaEventType


class GameNotReadyCheckAnswerTriviaEvent(AbsTriviaEvent):

    def __init__(
        self,
        actionId: str,
        answer: str,
        twitchChannel: str,
        userId: str,
        userName: str
    ):
        super().__init__(
            actionId = actionId,
            triviaEventType = TriviaEventType.GAME_NOT_READY
        )

        if not utils.isValidStr(twitchChannel):
            raise ValueError(f'twitchChannel argument is malformed: \"{twitchChannel}\"')
        elif not utils.isValidStr(userId):
            raise ValueError(f'userId argument is malformed: \"{userId}\"')
        elif not utils.isValidStr(userName):
            raise ValueError(f'userName argument is malformed: \"{userName}\"')

        self.__answer: str = answer
        self.__twitchChannel: str = twitchChannel
        self.__userId: str = userId
        self.__userName: str = userName

    def getAnswer(self) -> str:
        return self.__answer

    def getTwitchChannel(self) -> str:
        return self.__twitchChannel

    def getUserId(self) -> str:
        return self.__userId

    def getUserName(self) -> str:
        return self.__userName

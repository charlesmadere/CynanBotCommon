try:
    import CynanBotCommon.utils as utils
    from CynanBotCommon.trivia.absTriviaEvent import AbsTriviaEvent
    from CynanBotCommon.trivia.triviaEventType import TriviaEventType
except:
    import utils

    from trivia.absTriviaEvent import AbsTriviaEvent
    from trivia.triviaEventType import TriviaEventType


class SuperGameNotReadyCheckAnswerTriviaEvent(AbsTriviaEvent):

    def __init__(
        self,
        answer: str,
        twitchChannel: str
    ):
        super().__init__(triviaEventType = TriviaEventType.SUPER_GAME_NOT_READY)

        if not utils.isValidStr(twitchChannel):
            raise ValueError(f'twitchChannel argument is malformed: \"{twitchChannel}\"')

        self.__answer: str = answer
        self.__twitchChannel: str = twitchChannel

    def getAnswer(self) -> str:
        return self.__answer

    def getTwitchChannel(self) -> str:
        return self.__twitchChannel

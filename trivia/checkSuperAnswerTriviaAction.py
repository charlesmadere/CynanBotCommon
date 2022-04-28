try:
    import CynanBotCommon.utils as utils
    from CynanBotCommon.trivia.absTriviaAction import AbsTriviaAction
    from CynanBotCommon.trivia.triviaActionType import TriviaActionType
except:
    import utils

    from trivia.absTriviaAction import AbsTriviaAction
    from trivia.triviaActionType import TriviaActionType


class CheckSuperAnswerTriviaAction(AbsTriviaAction):

    def __init__(
        self,
        answer: str,
        twitchChannel: str,
        userId: str,
        userName: str
    ):
        super().__init__(triviaActionType = TriviaActionType.CHECK_SUPER_ANSWER)

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

try:
    import CynanBotCommon.utils as utils
except:
    import utils


class AdditionalTriviaAnswer():

    def __init__(self, additionalTriviaAnswer: str, userId: str, userName: str):
        if not utils.isValidStr(additionalTriviaAnswer):
            raise ValueError(f'additionalTriviaAnswer argument is malformed: \"{additionalTriviaAnswer}\"')
        elif not utils.isValidStr(userId):
            raise ValueError(f'userId argument is malformed: \"{userId}\"')
        elif not utils.isValidStr(userName):
            raise ValueError(f'userName argument is malformed: \"{userName}\"')

        self.__additionalTriviaAnswer: str = additionalTriviaAnswer
        self.__userId: str = userId
        self.__userName: str = userName

    def getAdditionalTriviaAnswer(self) -> str:
        return self.__additionalTriviaAnswer

    def getUserId(self) -> str:
        return self.__userId

    def getUserName(self) -> str:
        return self.__userName

    def __str__(self) -> str:
        return f'additionalTriviaAnswer=\"{self.__additionalTriviaAnswer}\", userId=\"{self.__userId}\", userName=\"{self.__userName}\"'

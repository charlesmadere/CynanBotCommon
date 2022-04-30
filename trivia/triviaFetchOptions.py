try:
    import CynanBotCommon.utils as utils
    from CynanBotCommon.trivia.questionAnswerTriviaConditions import \
        QuestionAnswerTriviaConditions
except:
    import utils

    from trivia.questionAnswerTriviaConditions import \
        QuestionAnswerTriviaConditions


class TriviaFetchOptions():

    def __init__(
        self,
        twitchChannel: str,
        isJokeTriviaRepositoryEnabled: bool = False,
        questionAnswerTriviaConditions: QuestionAnswerTriviaConditions = QuestionAnswerTriviaConditions.NOT_ALLOWED
    ):
        if not utils.isValidStr(twitchChannel):
            raise ValueError(f'twitchChannel argument is malformed: \"{twitchChannel}\"')
        elif not utils.isValidBool(isJokeTriviaRepositoryEnabled):
            raise ValueError(f'isJokeTriviaRepositoryEnabled argument is malformed: \"{isJokeTriviaRepositoryEnabled}\"')
        elif questionAnswerTriviaConditions is None:
            raise ValueError(f'questionAnswerTriviaConditions argument is malformed: \"{questionAnswerTriviaConditions}\"')

        self.__twitchChannel: str = twitchChannel
        self.__isJokeTriviaRepositoryEnabled: bool = isJokeTriviaRepositoryEnabled
        self.__questionAnswerTriviaConditions: QuestionAnswerTriviaConditions = questionAnswerTriviaConditions

    def areQuestionAnswerTriviaQuestionsEnabled(self) -> bool:
        return self.__questionAnswerTriviaConditions is QuestionAnswerTriviaConditions.ALLOWED \
            or self.__questionAnswerTriviaConditions is QuestionAnswerTriviaConditions.REQUIRED

    def getTwitchChannel(self) -> str:
        return self.__twitchChannel

    def isJokeTriviaRepositoryEnabled(self) -> bool:
        return self.__isJokeTriviaRepositoryEnabled

    def requireQuestionAnswerTriviaQuestion(self) -> bool:
        return self.__questionAnswerTriviaConditions is QuestionAnswerTriviaConditions.REQUIRED

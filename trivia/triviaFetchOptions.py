try:
    import CynanBotCommon.utils as utils
except:
    import utils


class TriviaFetchOptions():

    def __init__(
        self,
        twitchChannel: str,
        areQuestionAnswerTriviaQuestionsEnabled: bool = False,
        isJokeTriviaRepositoryEnabled: bool = False,
        requireQuestionAnswerTriviaQuestion: bool = False
    ):
        if not utils.isValidStr(twitchChannel):
            raise ValueError(f'twitchChannel argument is malformed: \"{twitchChannel}\"')
        elif not utils.isValidBool(areQuestionAnswerTriviaQuestionsEnabled):
            raise ValueError(f'areQuestionAnswerTriviaQuestionsEnabled argument is malformed: \"{areQuestionAnswerTriviaQuestionsEnabled}\"')
        elif not utils.isValidBool(isJokeTriviaRepositoryEnabled):
            raise ValueError(f'isJokeTriviaRepositoryEnabled argument is malformed: \"{isJokeTriviaRepositoryEnabled}\"')
        elif not utils.isValidBool(requireQuestionAnswerTriviaQuestion):
            raise ValueError(f'requireQuestionAnswerTriviaQuestion argument is malformed: \"{requireQuestionAnswerTriviaQuestion}\"')

        self.__twitchChannel: str = twitchChannel
        self.__areQuestionAnswerTriviaQuestionsEnabled: bool = areQuestionAnswerTriviaQuestionsEnabled
        self.__isJokeTriviaRepositoryEnabled: bool = isJokeTriviaRepositoryEnabled
        self.__requireQuestionAnswerTriviaQuestion: bool = requireQuestionAnswerTriviaQuestion

    def areQuestionAnswerTriviaQuestionsEnabled(self) -> bool:
        return self.__areQuestionAnswerTriviaQuestionsEnabled

    def getTwitchChannel(self) -> str:
        return self.__twitchChannel

    def isJokeTriviaRepositoryEnabled(self) -> bool:
        return self.__isJokeTriviaRepositoryEnabled

    def requireQuestionAnswerTriviaQuestion(self) -> bool:
        return self.__areQuestionAnswerTriviaQuestionsEnabled and self.__requireQuestionAnswerTriviaQuestion

try:
    import CynanBotCommon.utils as utils
    from CynanBotCommon.trivia.triviaSource import TriviaSource
except:
    import utils

    from trivia.triviaSource import TriviaSource


class TriviaQuestionReference():

    def __init__(self, triviaId: str, twitchChannel: str, triviaSource: TriviaSource):
        if not utils.isValidStr(triviaId):
            raise ValueError(f'triviaId argument is malformed: \"{triviaId}\"')
        elif not utils.isValidStr(twitchChannel):
            raise ValueError(f'twitchChannel argument is malformed: \"{twitchChannel}\"')
        elif triviaSource is None:
            raise ValueError(f'triviaSource argument is malformed: \"{triviaSource}\"')

        self.__triviaId: str = triviaId
        self.__twitchChannel: str = twitchChannel
        self.__triviaSource: TriviaSource = triviaSource

    def getTriviaId(self) -> str:
        return self.__triviaId

    def getTriviaSource(self) -> TriviaSource:
        return self.__triviaSource

    def getTwitchChannel(self) -> str:
        return self.__twitchChannel

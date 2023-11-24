try:
    import CynanBotCommon.utils as utils
    from CynanBotCommon.trivia.absTriviaAction import AbsTriviaAction
    from CynanBotCommon.trivia.triviaActionType import TriviaActionType
except:
    import utils
    from trivia.absTriviaAction import AbsTriviaAction
    from trivia.triviaActionType import TriviaActionType


class ClearSuperTriviaQueueTriviaAction(AbsTriviaAction):

    def __init__(self, twitchChannel: str):
        super().__init__(triviaActionType = TriviaActionType.CLEAR_SUPER_TRIVIA_QUEUE)

        if not utils.isValidStr(twitchChannel):
            raise ValueError(f'twitchChannel argument is malformed: \"{twitchChannel}\"')

        self.__twitchChannel: str = twitchChannel

    def getTwitchChannel(self) -> str:
        return self.__twitchChannel

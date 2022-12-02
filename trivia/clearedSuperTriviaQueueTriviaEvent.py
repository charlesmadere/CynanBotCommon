try:
    import CynanBotCommon.utils as utils
    from CynanBotCommon.trivia.absTriviaEvent import AbsTriviaEvent
    from CynanBotCommon.trivia.triviaEventType import TriviaEventType
except:
    import utils
    from trivia.absTriviaEvent import AbsTriviaEvent
    from trivia.triviaEventType import TriviaEventType


class ClearedSuperTriviaQueueTriviaEvent(AbsTriviaEvent):

    def __init__(
        self,
        numberOfGamesRemoved: int,
        actionId: str,
        twitchChannel: str
    ):
        super().__init__(
            actionId = actionId,
            triviaEventType = TriviaEventType.CLEARED_SUPER_TRIVIA_QUEUE
        )

        if not utils.isValidNum(numberOfGamesRemoved):
            raise ValueError(f'numberOfGamesRemoved argument is malformed: \"{numberOfGamesRemoved}\"')
        elif not utils.isValidStr(twitchChannel):
            raise ValueError(f'twitchChannel argument is malformed: \"{twitchChannel}\"')

        self.__numberOfGamesRemoved: int = numberOfGamesRemoved
        self.__twitchChannel: str = twitchChannel

    def getNumberOfGamesRemoved(self) -> int:
        return self.__numberOfGamesRemoved

    def getTwitchChannel(self) -> str:
        return self.__twitchChannel

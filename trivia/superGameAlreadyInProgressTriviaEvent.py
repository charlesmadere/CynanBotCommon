try:
    import CynanBotCommon.utils as utils
    from CynanBotCommon.trivia.absTriviaEvent import AbsTriviaEvent
    from CynanBotCommon.trivia.triviaEventType import TriviaEventType
except:
    import utils

    from trivia.absTriviaEvent import AbsTriviaEvent
    from trivia.triviaEventType import TriviaEventType


class SuperGameAlreadyInProgressTriviaEvent(AbsTriviaEvent):

    def __init__(
        self,
        gameId: str,
        twitchChannel: str
    ):
        super().__init__(triviaEventType = TriviaEventType.SUPER_GAME_ALREADY_IN_PROGRESS)

        if not utils.isValidStr(gameId):
            raise ValueError(f'gameId argument is malformed: \"{gameId}\"')
        elif not utils.isValidStr(twitchChannel):
            raise ValueError(f'twitchChannel argument is malformed: \"{twitchChannel}\"')

        self.__gameId: str = gameId
        self.__twitchChannel: str = twitchChannel

    def getGameId(self) -> str:
        return self.__gameId

    def getTwitchChannel(self) -> str:
        return self.__twitchChannel

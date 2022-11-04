import locale

try:
    import CynanBotCommon.utils as utils
    from CynanBotCommon.trivia.absTriviaEvent import AbsTriviaEvent
    from CynanBotCommon.trivia.triviaEventType import TriviaEventType
except:
    import utils
    from trivia.absTriviaEvent import AbsTriviaEvent
    from trivia.triviaEventType import TriviaEventType


class SuperGameLaunchpadTriviaEvent(AbsTriviaEvent):

    def __init__(
        self,
        remainingQueueSize: int,
        actionId: str,
        twitchChannel: str
    ):
        super().__init__(
            actionId = actionId,
            triviaEventType = TriviaEventType.SUPER_GAME_LAUNCHPAD
        )

        if not utils.isValidNum(remainingQueueSize):
            raise ValueError(f'remainingQueueSize argument is malformed: \"{remainingQueueSize}\"')
        elif remainingQueueSize < 0 or remainingQueueSize >= utils.getIntMaxSafeSize():
            raise ValueError(f'remainingQueueSize argument is out of bounds: {remainingQueueSize}')
        elif not utils.isValidStr(twitchChannel):
            raise ValueError(f'twitchChannel argument is malformed: \"{twitchChannel}\"')

        self.__remainingQueueSize: int = remainingQueueSize
        self.__twitchChannel: str = twitchChannel

    def getRemainingQueueSize(self) -> int:
        return self.__remainingQueueSize

    def getRemainingQueueSizeStr(self) -> str:
        return locale.format_string("%d", self.__remainingQueueSize, grouping = True)

    def getTwitchChannel(self) -> str:
        return self.__twitchChannel

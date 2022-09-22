from typing import List, Optional

try:
    import CynanBotCommon.utils as utils
    from CynanBotCommon.trivia.startNewSuperTriviaGameAction import \
        StartNewSuperTriviaGameAction
    from CynanBotCommon.trivia.triviaSettingsRepository import \
        TriviaSettingsRepository
except:
    import utils

    from trivia.startNewSuperTriviaGameAction import \
        StartNewSuperTriviaGameAction
    from trivia.triviaSettingsRepository import TriviaSettingsRepository


class QueuedTriviaGameStore():

    def __init__(self, triviaSettingsRepository: TriviaSettingsRepository):
        if triviaSettingsRepository is None:
            raise ValueError(f'triviaSettingsRepository argument is malformed: \"{triviaSettingsRepository}\"')

        self.__triviaSettingsRepository: TriviaSettingsRepository = triviaSettingsRepository
        self.__queuedSuperGames: List[StartNewSuperTriviaGameAction] = list()

    async def add(self, action: StartNewSuperTriviaGameAction) -> bool:
        if action is None:
            raise ValueError(f'action argument is malformed: \"{action}\"')

        maxSuperGameQueueSize = await self.__triviaSettingsRepository.getMaxSuperGameQueueSize()
        currentQueueSize: int = 0

        for queuedSuperGame in self.__queuedSuperGames:
            if action.getTwitchChannel() == queuedSuperGame.getTwitchChannel():
                currentQueueSize = currentQueueSize + 1

        if currentQueueSize < maxSuperGameQueueSize:
            self.__queuedSuperGames.append(action)
            return True
        else:
            return False

    async def popQueuedSuperGame(self, twitchChannel: str) -> Optional[StartNewSuperTriviaGameAction]:
        if not utils.isValidStr(twitchChannel):
            raise ValueError(f'twitchChannel argument is malformed: \"{twitchChannel}\"')

        twitchChannel = twitchChannel.lower()

        for index, queuedSuperGame in enumerate(self.__queuedSuperGames):
            if twitchChannel == queuedSuperGame.getTwitchChannel():
                del self.__queuedSuperGames[index]
                return queuedSuperGame

        return None

from collections import defaultdict
from queue import SimpleQueue
from typing import Dict, List, Set

try:
    from CynanBotCommon.trivia.startNewSuperTriviaGameAction import \
        StartNewSuperTriviaGameAction
    from CynanBotCommon.trivia.triviaSettingsRepository import \
        TriviaSettingsRepository
except:
    from trivia.startNewSuperTriviaGameAction import \
        StartNewSuperTriviaGameAction
    from trivia.triviaSettingsRepository import TriviaSettingsRepository


class QueuedTriviaGameStore():

    def __init__(self, triviaSettingsRepository: TriviaSettingsRepository):
        if triviaSettingsRepository is None:
            raise ValueError(f'triviaSettingsRepository argument is malformed: \"{triviaSettingsRepository}\"')

        self.__triviaSettingsRepository: TriviaSettingsRepository = triviaSettingsRepository
        self.__queuedSuperGames: Dict[str, SimpleQueue[StartNewSuperTriviaGameAction]] = defaultdict(lambda: SimpleQueue())

    async def addSuperGame(self, action: StartNewSuperTriviaGameAction) -> bool:
        if action is None:
            raise ValueError(f'action argument is malformed: \"{action}\"')

        maxSuperGameQueueSize = await self.__triviaSettingsRepository.getMaxSuperGameQueueSize()

        if maxSuperGameQueueSize <= 0:
            return False

        twitchChannel = action.getTwitchChannel().lower()
        queuedSuperGames = self.__queuedSuperGames[twitchChannel]

        if queuedSuperGames.qsize() < maxSuperGameQueueSize:
            queuedSuperGames.put(action)
            return True
        else:
            return False

    async def popQueuedSuperGames(self, activeChannels: Set[str]) -> List[StartNewSuperTriviaGameAction]:
        workingActiveChannels: Set[str] = set()
        for activeChannel in activeChannels:
            workingActiveChannels.add(activeChannel.lower())

        superGames: List[StartNewSuperTriviaGameAction] = list()

        for twitchChannel, queuedSuperGames in self.__queuedSuperGames.items():
            if twitchChannel.lower() in workingActiveChannels:
                continue
            elif queuedSuperGames.empty():
                continue
            else:
                superGames.append(queuedSuperGames.get())

        return superGames

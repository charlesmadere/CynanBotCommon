from abc import ABC, abstractmethod
from typing import List, Set

try:
    from CynanBotCommon.trivia.addQueuedGamesResult import AddQueuedGamesResult
    from CynanBotCommon.trivia.clearQueuedGamesResult import \
        ClearQueuedGamesResult
    from CynanBotCommon.trivia.startNewSuperTriviaGameAction import \
        StartNewSuperTriviaGameAction
except:
    from trivia.addQueuedGamesResult import AddQueuedGamesResult
    from trivia.clearQueuedGamesResult import ClearQueuedGamesResult
    from trivia.startNewSuperTriviaGameAction import \
        StartNewSuperTriviaGameAction


class QueuedTriviaGameStoreInterface(ABC):

    @abstractmethod
    async def addSuperGames(
        self,
        isSuperTriviaGameCurrentlyInProgress: bool,
        action: StartNewSuperTriviaGameAction
    ) -> AddQueuedGamesResult:
        pass

    @abstractmethod
    async def clearQueuedSuperGames(self, twitchChannel: str) -> ClearQueuedGamesResult:
        pass

    @abstractmethod
    async def getQueuedSuperGamesSize(self, twitchChannel: str) -> int:
        pass

    @abstractmethod
    async def popQueuedSuperGames(self, activeChannels: Set[str]) -> List[StartNewSuperTriviaGameAction]:
        pass

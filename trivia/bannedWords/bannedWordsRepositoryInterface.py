from abc import ABC, abstractmethod
from typing import Set

try:
    from CynanBotCommon.trivia.bannedWords.absBannedWord import AbsBannedWord
except:
    from trivia.bannedWords.absBannedWord import AbsBannedWord


class BannedWordsRepositoryInterface(ABC):

    @abstractmethod
    async def clearCaches(self):
        pass

    @abstractmethod
    def getBannedWords(self) -> Set[AbsBannedWord]:
        pass

    @abstractmethod
    async def getBannedWordsAsync(self) -> Set[AbsBannedWord]:
        pass

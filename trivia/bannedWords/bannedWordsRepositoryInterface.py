from abc import ABC, abstractmethod
from typing import Set

try:
    from CynanBotCommon.trivia.bannedWords.bannedWord import BannedWord
except:
    from trivia.bannedWords.bannedWord import BannedWord


class BannedWordsRepositoryInterface(ABC):

    @abstractmethod
    async def clearCaches(self):
        pass

    @abstractmethod
    def getBannedWords(self) -> Set[BannedWord]:
        pass

    @abstractmethod
    async def getBannedWordsAsync(self) -> Set[BannedWord]:
        pass

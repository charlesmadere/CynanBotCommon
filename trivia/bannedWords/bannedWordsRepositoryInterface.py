from abc import abstractmethod
from typing import Set

try:
    from CynanBotCommon.clearable import Clearable
    from CynanBotCommon.trivia.bannedWords.absBannedWord import AbsBannedWord
except:
    from clearable import Clearable
    from trivia.bannedWords.absBannedWord import AbsBannedWord


class BannedWordsRepositoryInterface(Clearable):

    @abstractmethod
    def getBannedWords(self) -> Set[AbsBannedWord]:
        pass

    @abstractmethod
    async def getBannedWordsAsync(self) -> Set[AbsBannedWord]:
        pass

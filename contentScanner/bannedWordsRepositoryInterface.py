from abc import abstractmethod
from typing import Set

try:
    from CynanBotCommon.clearable import Clearable
    from CynanBotCommon.contentScanner.absBannedWord import AbsBannedWord
except:
    from clearable import Clearable
    from contentScanner.absBannedWord import AbsBannedWord


class BannedWordsRepositoryInterface(Clearable):

    @abstractmethod
    def getBannedWords(self) -> Set[AbsBannedWord]:
        pass

    @abstractmethod
    async def getBannedWordsAsync(self) -> Set[AbsBannedWord]:
        pass

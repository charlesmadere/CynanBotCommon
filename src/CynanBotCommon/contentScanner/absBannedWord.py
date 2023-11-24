from abc import ABC, abstractmethod

try:
    from CynanBotCommon.contentScanner.bannedWordType import BannedWordType
except:
    from contentScanner.bannedWordType import BannedWordType


class AbsBannedWord(ABC):

    @abstractmethod
    def getType(self) -> BannedWordType:
        pass

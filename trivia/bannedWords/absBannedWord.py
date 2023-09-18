from abc import ABC, abstractmethod

try:
    from CynanBotCommon.trivia.bannedWords.bannedWordType import BannedWordType
except:
    from trivia.bannedWords.bannedWordType import BannedWordType


class AbsBannedWord(ABC):

    @abstractmethod
    def getType(self) -> BannedWordType:
        pass

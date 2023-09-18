from typing import Any, List

try:
    import CynanBotCommon.utils as utils
    from CynanBotCommon.trivia.bannedWords.absBannedWord import AbsBannedWord
    from CynanBotCommon.trivia.bannedWords.bannedWordCheckType import \
        BannedWordCheckType
    from CynanBotCommon.trivia.bannedWords.bannedWordType import BannedWordType
except:
    import utils
    from trivia.bannedWords.absBannedWord import AbsBannedWord
    from trivia.bannedWords.bannedWordCheckType import BannedWordCheckType
    from trivia.bannedWords.bannedWordType import BannedWordType


class BannedWord(AbsBannedWord):

    def __init__(self, checkType: BannedWordCheckType, word: str):
        if not isinstance(checkType, BannedWordCheckType):
            raise ValueError(f'checkType argument is malformed: \"{checkType}\"')
        if not utils.isValidStr(word):
            raise ValueError(f'word argument is malformed: \"{word}\"')

        self.__checkType: BannedWordCheckType = checkType
        self.__words: List[str] = word.lower().split()
        self.__word: str = word.lower()

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, AbsBannedWord):
            if isinstance(other, BannedWord):
                return self.__checkType is other.__checkType and self.__word == other.__word
            else:
                return False
        else:
            raise ValueError(f'`other` is an unsupported type: \"{other}\"')

    def getCheckType(self) -> BannedWordCheckType:
        return self.__checkType

    def getType(self) -> BannedWordType:
        return BannedWordType.WORD

    def getWord(self) -> str:
        return self.__word

    def getWords(self) -> List[str]:
        return self.__words

    def __hash__(self) -> int:
        return hash((self.__checkType, self.__word))

    def isPhrase(self) -> bool:
        return len(self.__words) >= 2

    def __str__(self) -> str:
        return f'word=\"{self.__word}\", checkType=\"{self.__checkType}\"'

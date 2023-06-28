from typing import Any

try:
    import CynanBotCommon.utils as utils
    from CynanBotCommon.trivia.bannedWords.bannedWordCheckType import \
        BannedWordCheckType
except:
    import utils
    from trivia.bannedWords.bannedWordCheckType import BannedWordCheckType


class BannedWord():

    def __init__(self, checkType: BannedWordCheckType, word: str):
        if not isinstance(checkType, BannedWordCheckType):
            raise ValueError(f'checkType argument is malformed: \"{checkType}\"')
        if not utils.isValidStr(word):
            raise ValueError(f'word argument is malformed: \"{word}\"')

        self.__checkType: BannedWordCheckType = checkType
        self.__word: str = word.lower()

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, BannedWord):
            return self.__checkType is other.__checkType and self.__word == other.__word
        else:
            raise ValueError(f'`other` is an unsupported type: \"{other}\"')

    def getCheckType(self) -> BannedWordCheckType:
        return self.__checkType

    def getWord(self) -> str:
        return self.__word

    def __hash__(self) -> int:
        return hash((self.__checkType, self.__word))

    def __str__(self) -> str:
        return f'word=\"{self.__word}\", checkType={self.__checkType}'

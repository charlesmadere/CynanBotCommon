from typing import Any

try:
    import CynanBotCommon.utils as utils
    from CynanBotCommon.trivia.bannedWords.bannedWordCheckType import \
        BannedWordCheckType
except:
    import utils
    from trivia.bannedWords.bannedWordCheckType import BannedWordCheckType


class BannedWord():

    def __init__(
        self,
        bannedWordCheckType: BannedWordCheckType,
        word: str
    ):
        if not isinstance(bannedWordCheckType, BannedWordCheckType):
            raise ValueError(f'bannedWordCheckType argument is malformed: \"{bannedWordCheckType}\"')
        if not utils.isValidStr(word):
            raise ValueError(f'word argument is malformed: \"{word}\"')

        self.__bannedWordCheckType: BannedWordCheckType = bannedWordCheckType
        self.__word: str = word

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, BannedWord):
            return self.__word.lower() == other.__word.lower()
        else:
            raise ValueError(f'`other` is an unsupported type: \"{other}\"')

    def getBannedWordCheckType(self) -> BannedWordCheckType:
        return self.__bannedWordCheckType

    def getWord(self) -> str:
        return self.__word

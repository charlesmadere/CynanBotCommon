from typing import Any

try:
    import CynanBotCommon.utils as utils
    from CynanBotCommon.trivia.bannedWords.absBannedWord import AbsBannedWord
    from CynanBotCommon.trivia.bannedWords.bannedWordType import BannedWordType
except:
    import utils
    from trivia.bannedWords.absBannedWord import AbsBannedWord
    from trivia.bannedWords.bannedWordType import BannedWordType


class BannedWord(AbsBannedWord):

    def __init__(self, word: str):
        if not utils.isValidStr(word):
            raise ValueError(f'word argument is malformed: \"{word}\"')

        self.__word: str = word.lower()

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, AbsBannedWord):
            if isinstance(other, BannedWord):
                return self.__word == other.__word
            else:
                return False
        else:
            raise ValueError(f'`other` is an unsupported type: \"{other}\"')

    def getType(self) -> BannedWordType:
        return BannedWordType.WORD

    def getWord(self) -> str:
        return self.__word

    def __hash__(self) -> int:
        return hash((self.__word, self.getType()))

    def __str__(self) -> str:
        return f'word=\"{self.__word}\", type=\"{self.getType()}\"'

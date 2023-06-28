import re
import traceback
from typing import List, Optional, Pattern, Set

try:
    import CynanBotCommon.utils as utils
    from CynanBotCommon.storage.linesReaderInterface import \
        LinesReaderInterface
    from CynanBotCommon.timber.timber import Timber
    from CynanBotCommon.trivia.bannedWords.bannedWord import BannedWord
    from CynanBotCommon.trivia.bannedWords.bannedWordCheckType import \
        BannedWordCheckType
    from CynanBotCommon.trivia.bannedWords.bannedWordsRepositoryInterface import \
        BannedWordsRepositoryInterface
except:
    import utils
    from storage.linesReaderInterface import LinesReaderInterface
    from timber.timber import Timber
    from trivia.bannedWords.bannedWord import BannedWord
    from trivia.bannedWords.bannedWordCheckType import BannedWordCheckType
    from trivia.bannedWords.bannedWordsRepositoryInterface import \
        BannedWordsRepositoryInterface


class BannedWordsRepository(BannedWordsRepositoryInterface):

    def __init__(
        self,
        bannedWordsLinesReader: LinesReaderInterface,
        timber: Timber
    ):
        if not isinstance(bannedWordsLinesReader, LinesReaderInterface):
            raise ValueError(f'bannedWordsLinesReader argument is malformed: \"{bannedWordsLinesReader}\"')
        elif not isinstance(timber, Timber):
            raise ValueError(f'timber argument is malformed: \"{timber}\"')

        self.__bannedWordsLinesReader: LinesReaderInterface = bannedWordsLinesReader
        self.__timber: Timber = timber

        self.__quoteRegEx: Pattern = re.compile(r'^"(.+)"$', re.IGNORECASE)
        self.__cache: Optional[Set[BannedWord]] = None

    async def clearCaches(self):
        self.__cache = None

    def __createCleanedBannedWordsSetFromLines(
        self,
        lines: Optional[List[Optional[str]]]
    ) -> Set[BannedWord]:
        cleanedBannedWords: Set[str] = set()

        if not utils.hasItems(lines):
            return cleanedBannedWords

        for line in lines:
            bannedWord = self.__processLine(line)

            if bannedWord is not None:
                cleanedBannedWords.add(bannedWord)

        return cleanedBannedWords

    def __fetchBannedWords(self) -> Set[BannedWord]:
        lines: Optional[List[Optional[str]]] = None

        try:
            lines = self.__bannedWordsLinesReader.readLines()
        except FileNotFoundError as e:
            self.__timber.log('BannedWordsRepository', f'Banned words file not found when trying to synchronously read from banned words file', e, traceback.format_exc())
            raise FileNotFoundError('Banned words file not found when trying to synchronously read from banned words file')

        return self.__createCleanedBannedWordsSetFromLines(lines)

    async def __fetchBannedWordsAsync(self) -> Set[BannedWord]:
        lines: Optional[List[Optional[str]]] = None

        try:
            lines = await self.__bannedWordsLinesReader.readLinesAsync()
        except FileNotFoundError as e:
            self.__timber.log('BannedWordsRepository', 'Banned words file not found when trying to asynchronously read from banned words file', e, traceback.format_exc())
            raise FileNotFoundError('Banned words file not found when trying to asynchronously read from banned words file')

        return self.__createCleanedBannedWordsSetFromLines(lines)

    def getBannedWords(self) -> Set[BannedWord]:
        if self.__cache is not None:
            return self.__cache

        bannedWords = self.__fetchBannedWords()
        self.__cache = bannedWords
        self.__timber.log('BannedWordsRepository', f'Synchronously read in {len(bannedWords)} banned word(s)')

        return bannedWords

    async def getBannedWordsAsync(self) -> Set[BannedWord]:
        if self.__cache is not None:
            return self.__cache

        bannedWords = await self.__fetchBannedWordsAsync()
        self.__cache = bannedWords
        self.__timber.log('BannedWordsRepository', f'Asynchronously read in {len(bannedWords)} banned word(s)')

        return bannedWords

    def __processLine(self, line: Optional[str]) -> Optional[BannedWord]:
        if not utils.isValidStr(line):
            return None

        word = line.strip().lower()

        if not utils.isValidStr(word):
            return None

        quoteRegExMatch = self.__quoteRegEx.fullmatch(word)
        checkType = BannedWordCheckType.ANYWHERE

        if quoteRegExMatch is not None:
            word = quoteRegExMatch.group(1).strip()
            checkType = BannedWordCheckType.EXACT_MATCH

        return BannedWord(
            checkType = checkType,
            word = word
        )

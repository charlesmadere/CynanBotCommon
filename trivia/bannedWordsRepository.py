import os
import re
from typing import List, Optional, Pattern, Set

import aiofiles
import aiofiles.ospath

try:
    import CynanBotCommon.utils as utils
    from CynanBotCommon.timber.timber import Timber
except:
    import utils
    from timber.timber import Timber


class BannedWordsRepository():

    def __init__(
        self,
        timber: Timber,
        bannedWordsFile: str = 'CynanBotCommon/trivia/bannedWords.txt'
    ):
        if not isinstance(timber, Timber):
            raise ValueError(f'timber argument is malformed: \"{timber}\"')
        elif not utils.isValidStr(bannedWordsFile):
            raise ValueError(f'bannedWordsFile argument is malformed: \"{bannedWordsFile}\"')

        self.__timber: Timber = timber
        self.__bannedWordsFile: str = bannedWordsFile

        self.__quoteRegEx: Pattern = re.compile(r'^".+"$', re.IGNORECASE)
        self.__bannedWordsCache: Optional[Set[str]] = None

    async def clearCaches(self):
        self.__bannedWordsCache = None
        self.__timber.log('BannedWordsRepository', 'Caches cleared')

    def __createCleanedBannedWordsSetFromLines(
        self,
        lines: Optional[List[Optional[str]]]
    ) -> Set[str]:
        cleanedBannedWords: Set[str] = set()

        if not utils.hasItems(lines):
            return cleanedBannedWords

        for line in lines:
            processedLine = self.__processWord(line)

            if utils.isValidStr(processedLine):
                cleanedBannedWords.add(processedLine)

        return cleanedBannedWords

    def __fetchBannedWords(self) -> Set[str]:
        if not os.path.exists(self.__bannedWordsFile):
            raise FileNotFoundError(f'Banned words file not found: \"{self.__bannedWordsFile}\"')

        lines: Optional[List[str]] = None

        with open(self.__bannedWordsFile, 'r') as file:
            lines = file.readlines()

        return self.__createCleanedBannedWordsSetFromLines(lines)

    async def __fetchBannedWordsAsync(self) -> Set[str]:
        if not await aiofiles.ospath.exists(self.__bannedWordsFile):
            raise FileNotFoundError(f'Banned words file not found: \"{self.__bannedWordsFile}\"')

        lines: Optional[List[str]] = None

        async with aiofiles.open(self.__bannedWordsFile, 'r') as file:
            lines = await file.readlines()

        return self.__createCleanedBannedWordsSetFromLines(lines)

    def getBannedWords(self) -> Set[str]:
        if self.__bannedWordsCache is not None:
            return self.__bannedWordsCache

        bannedWords = self.__fetchBannedWords()
        self.__timber.log('BannedWordsRepository', f'Synchronously read in {len(bannedWords)} banned word(s) from \"{self.__bannedWordsFile}\"')
        self.__bannedWordsCache = bannedWords

        return bannedWords

    async def getBannedWordsAsync(self) -> Set[str]:
        if self.__bannedWordsCache is not None:
            return self.__bannedWordsCache

        bannedWords = await self.__fetchBannedWordsAsync()
        self.__timber.log('BannedWordsRepository', f'Asynchronously read in {len(bannedWords)} banned word(s) from \"{self.__bannedWordsFile}\"')
        self.__bannedWordsCache = bannedWords

        return bannedWords

    def __processWord(self, line: Optional[str]) -> Optional[str]:
        if not utils.isValidStr(line):
            return None

        line = line.strip().lower()

        if not utils.isValidStr(line):
            return None

        quoteRegExMatch = self.__quoteRegEx.fullmatch(line)
        if quoteRegExMatch is not None:
            line = quoteRegExMatch.group(1).strip()

        return line

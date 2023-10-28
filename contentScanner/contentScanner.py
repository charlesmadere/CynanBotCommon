import re
from typing import Optional, Pattern, Set

try:
    import CynanBotCommon.utils as utils
    from CynanBotCommon.contentScanner.bannedWordsRepositoryInterface import \
        BannedWordsRepositoryInterface
    from CynanBotCommon.contentScanner.contentCode import ContentCode
    from CynanBotCommon.contentScanner.contentScannerInterface import \
        ContentScannerInterface
    from CynanBotCommon.timber.timberInterface import TimberInterface
except:
    import utils
    from contentScanner.bannedWordsRepositoryInterface import \
        BannedWordsRepositoryInterface
    from contentScanner.contentCode import ContentCode
    from contentScanner.contentScannerInterface import ContentScannerInterface
    from timber.timberInterface import TimberInterface


class ContentScanner(ContentScannerInterface):

    def __init__(
        self,
        bannedWordsRepository: BannedWordsRepositoryInterface,
        timber: TimberInterface
    ):
        if not isinstance(bannedWordsRepository, BannedWordsRepositoryInterface):
            raise ValueError(f'bannedWordsRepository argument is malformed: \"{bannedWordsRepository}\"')
        elif not isinstance(timber, TimberInterface):
            raise ValueError(f'timber argument is malformed: \"{timber}\"')

        self.__bannedWordsRepository: BannedWordsRepositoryInterface = bannedWordsRepository
        self.__timber: TimberInterface = timber

        self.__phraseRegEx: Pattern = re.compile(r'[a-z]+', re.IGNORECASE)
        self.__wordRegEx: Pattern = re.compile(r'\w', re.IGNORECASE)

    async def scan(self, message: Optional[str]) -> ContentCode:
        if not utils.isValidStr(message):
            # TODO
            return

        # TODO
        pass

    async def __updateQuestionPhrasesContent(
        self,
        phrases: Set[str],
        string: Optional[str]
    ):
        if not isinstance(phrases, Set):
            raise ValueError(f'phrases argument is malformed: \"{phrases}\"')

        if not utils.isValidStr(string):
            return

        string = string.lower()
        words = self.__phraseRegEx.findall(string)

        if not utils.hasItems(words):
            return

        phrase = ' '.join(words)
        phrases.add(phrase)

    async def __updateQuestionWordsContent(
        self,
        words: Set[Optional[str]],
        string: Optional[str]
    ):
        if not isinstance(words, Set):
            raise ValueError(f'words argument is malformed: \"{words}\"')

        if not utils.isValidStr(string):
            return

        splits = string.lower().split()

        if not utils.hasItems(splits):
            return

        for split in splits:
            words.add(split)
            characters = self.__wordRegEx.findall(split)

            if not utils.hasItems(characters):
                continue

            word = ''.join(characters)
            words.add(word)

import os
import re
from typing import List, Optional, Pattern

try:
    import CynanBotCommon.utils as utils
    from CynanBotCommon.tts.ttsCommandBuilderInterface import \
        TtsCommandBuilderInterface
except:
    import utils
    from tts.ttsCommandBuilderInterface import TtsCommandBuilderInterface


class DecTalkCommandBuilder(TtsCommandBuilderInterface):

    def __init__(
        self,
        pathToDecTalk: str = '../dectalk/say.exe'
    ):
        if not utils.isValidStr(pathToDecTalk):
            raise ValueError(f'pathToDecTalk argument is malformed: \"{pathToDecTalk}\"')

        self.__pathToDecTalk: str = self.__normalizePathToDecTalk(pathToDecTalk)
        self.__bannedStrings: List[Pattern] = self.__buildBannedStrings()
        self.__whiteSpaceRegEx: Pattern = re.compile(r'\s{2,}', re.IGNORECASE)

    async def buildAndCleanCommand(self, command: Optional[str]) -> Optional[str]:
        if not utils.isValidStr(command):
            return None

        command = command.strip()

        for bannedPhrase in self.__bannedStrings:
            command = bannedPhrase.sub('', command)

            if not utils.isValidStr(command):
                return None

        if not utils.isValidStr(command):
            return None

        # remove extranneous whitespace
        command = self.__whiteSpaceRegEx.sub(' ', command)
        command = command.strip()

        return f'{self.__pathToDecTalk} {command}'

    def __buildBannedStrings(self) -> List[Pattern]:
        bannedPhrases: List[Pattern] = list()

        # purge potentially dangerous/tricky characters
        bannedPhrases.append(re.compile(r'\&|\;|\||\^', re.IGNORECASE))

        # purge what might be directory traversal sequences
        bannedPhrases.append(re.compile(r'\.{2,}', re.IGNORECASE))

        # purge various help flags
        bannedPhrases.append(re.compile(r'(^|\s+)-h', re.IGNORECASE))
        bannedPhrases.append(re.compile(r'(^|\s+)-\?', re.IGNORECASE))

        # purge various input flags
        bannedPhrases.append(re.compile(r'(^|\s+)-pre', re.IGNORECASE))
        bannedPhrases.append(re.compile(r'(^|\s+)-post', re.IGNORECASE))
        bannedPhrases.append(re.compile(r'^\s*text', re.IGNORECASE))

        # purge various output flags
        bannedPhrases.append(re.compile(r'(^|\s+)-w', re.IGNORECASE))
        bannedPhrases.append(re.compile(r'(^|\s+)-l((\[\w+\])|\w+)?', re.IGNORECASE))

        return bannedPhrases

    def __normalizePathToDecTalk(self, pathToDecTalk: str) -> str:
        if not utils.isValidStr(pathToDecTalk):
            raise ValueError(f'pathToDecTalk argument is malformed: \"{pathToDecTalk}\"')

        return os.path.normcase(os.path.normpath(pathToDecTalk))

import re
from typing import List, Optional, Pattern

try:
    import CynanBotCommon.utils as utils
    from CynanBotCommon.contentScanner.contentCode import ContentCode
    from CynanBotCommon.contentScanner.contentScannerInterface import \
        ContentScannerInterface
    from CynanBotCommon.timber.timberInterface import TimberInterface
    from CynanBotCommon.tts.ttsCommandBuilderInterface import \
        TtsCommandBuilderInterface
    from CynanBotCommon.tts.ttsSettingsRepositoryInterface import \
        TtsSettingsRepositoryInterface
except:
    import utils
    from contentScanner.contentCode import ContentCode
    from contentScanner.contentScannerInterface import ContentScannerInterface
    from timber.timberInterface import TimberInterface
    from tts.ttsCommandBuilderInterface import TtsCommandBuilderInterface
    from tts.ttsSettingsRepositoryInterface import \
        TtsSettingsRepositoryInterface


class DecTalkCommandBuilder(TtsCommandBuilderInterface):

    def __init__(
        self,
        contentScanner: ContentScannerInterface,
        timber: TimberInterface,
        ttsSettingsRepository: TtsSettingsRepositoryInterface
    ):
        if not isinstance(contentScanner, ContentScannerInterface):
            raise ValueError(f'contentScanner argument is malformed: \"{contentScanner}\"')
        elif not isinstance(timber, TimberInterface):
            raise ValueError(f'timber argument is malformed: \"{timber}\"')
        elif not isinstance(ttsSettingsRepository, TtsSettingsRepositoryInterface):
            raise ValueError(f'ttsSettingsRepository argument is malformed: \"{ttsSettingsRepository}\"')

        self.__contentScanner: ContentScannerInterface = contentScanner
        self.__timber: TimberInterface = timber
        self.__ttsSettingsRepository: TtsSettingsRepositoryInterface = ttsSettingsRepository

        self.__bannedStrings: List[Pattern] = self.__buildBannedStrings()
        self.__whiteSpaceRegEx: Pattern = re.compile(r'\s{2,}', re.IGNORECASE)

    async def buildAndCleanCommand(self, command: Optional[str]) -> Optional[str]:
        if not utils.isValidStr(command):
            return None

        for bannedString in self.__bannedStrings:
            command = bannedString.sub('', command)

            if not utils.isValidStr(command):
                return None

        if not utils.isValidStr(command):
            return None

        command = command.strip()
        contentCode = await self.__contentScanner.scan(command)

        if contentCode is not ContentCode.OK:
            self.__timber.log('DecTalkCommandBuilder', f'TTS command \"{command}\" returned a bad content code: \"{contentCode}\"')
            return None

        maxMessageSize = await self.__ttsSettingsRepository.getMaximumMessageSize()

        if len(command) > maxMessageSize:
            self.__timber.log('DecTalkCommandBuilder', f'Chopping down TTS command \"{command}\" as it is too long (len={len(command)}) ({maxMessageSize=}) ({command})')
            command = command[:maxMessageSize]

        # remove extranneous whitespace
        command = self.__whiteSpaceRegEx.sub(' ', command)
        command = command.strip()

        if not utils.isValidStr(command):
            return None

        return command

    def __buildBannedStrings(self) -> List[Pattern]:
        bannedPhrases: List[Pattern] = list()

        # purge potentially dangerous/tricky characters
        bannedPhrases.append(re.compile(r'\&|\%|\;|\=|\'|\"|\||\^|\~', re.IGNORECASE))

        # purge what might be directory traversal sequences
        bannedPhrases.append(re.compile(r'\.{2,}', re.IGNORECASE))

        # purge various help flags
        bannedPhrases.append(re.compile(r'(^|\s+)-h', re.IGNORECASE))
        bannedPhrases.append(re.compile(r'(^|\s+)-\?', re.IGNORECASE))

        # purge various input flags
        bannedPhrases.append(re.compile(r'(^|\s+)-pre', re.IGNORECASE))
        bannedPhrases.append(re.compile(r'(^|\s+)-post', re.IGNORECASE))
        bannedPhrases.append(re.compile(r'^\s*text', re.IGNORECASE))

        # purge user dictionary flag
        bannedPhrases.append(re.compile(r'(^|\s+)-d', re.IGNORECASE))

        # purge version information flag
        bannedPhrases.append(re.compile(r'(^|\s+)-v', re.IGNORECASE))

        # purge language flag
        bannedPhrases.append(re.compile(r'(^|\s+)-lang(\s+\w+)?', re.IGNORECASE))

        # purge various output flags
        bannedPhrases.append(re.compile(r'(^|\s+)-w', re.IGNORECASE))
        bannedPhrases.append(re.compile(r'(^|\s+)-l((\[\w+\])|\w+)?', re.IGNORECASE))

        return bannedPhrases

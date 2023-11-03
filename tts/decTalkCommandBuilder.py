import re
from typing import List, Optional, Pattern

try:
    import CynanBotCommon.utils as utils
    from CynanBotCommon.contentScanner.contentCode import ContentCode
    from CynanBotCommon.contentScanner.contentScannerInterface import \
        ContentScannerInterface
    from CynanBotCommon.timber.timberInterface import TimberInterface
    from CynanBotCommon.tts.ttsCheerDonation import TtsCheerDonation
    from CynanBotCommon.tts.ttsCommandBuilderInterface import \
        TtsCommandBuilderInterface
    from CynanBotCommon.tts.ttsDonation import TtsDonation
    from CynanBotCommon.tts.ttsEvent import TtsEvent
    from CynanBotCommon.tts.ttsSettingsRepositoryInterface import \
        TtsSettingsRepositoryInterface
    from CynanBotCommon.tts.ttsSubscriptionDonation import \
        TtsSubscriptionDonation
except:
    import utils
    from contentScanner.contentCode import ContentCode
    from contentScanner.contentScannerInterface import ContentScannerInterface
    from timber.timberInterface import TimberInterface
    from tts.ttsCheerDonation import TtsCheerDonation
    from tts.ttsCommandBuilderInterface import TtsCommandBuilderInterface
    from tts.ttsDonation import TtsDonation
    from tts.ttsEvent import TtsEvent
    from tts.ttsSettingsRepositoryInterface import \
        TtsSettingsRepositoryInterface
    from tts.ttsSubscriptionDonation import TtsSubscriptionDonation


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

    async def buildAndCleanEvent(self, event: Optional[TtsEvent]) -> Optional[str]:
        if event is None:
            return None
        if not isinstance(event, TtsEvent):
            raise ValueError(f'event argument is malformed: \"{event}\"')

        message = event.getMessage()

        if utils.isValidStr(message):
            message = await self.buildAndCleanMessage(message)

            if utils.isValidStr(message):
                return message

        # TODO
        pass

    async def buildAndCleanMessage(self, message: Optional[str]) -> Optional[str]:
        if not utils.isValidStr(message):
            return None

        for bannedString in self.__bannedStrings:
            message = bannedString.sub('', message)

            if not utils.isValidStr(message):
                return None

        if not utils.isValidStr(message):
            return None

        message = message.strip()
        contentCode = await self.__contentScanner.scan(message)

        if contentCode is not ContentCode.OK:
            self.__timber.log('DecTalkCommandBuilder', f'TTS command \"{message}\" returned a bad content code: \"{contentCode}\"')
            return None

        maxMessageSize = await self.__ttsSettingsRepository.getMaximumMessageSize()

        if len(message) > maxMessageSize:
            self.__timber.log('DecTalkCommandBuilder', f'Chopping down TTS command \"{message}\" as it is too long (len={len(message)}) ({maxMessageSize=}) ({message})')
            message = message[:maxMessageSize]

        # remove extranneous whitespace
        message = self.__whiteSpaceRegEx.sub(' ', message)
        message = message.strip()

        if not utils.isValidStr(message):
            return None

        return message

    def __buildBannedStrings(self) -> List[Pattern]:
        bannedStrings: List[Pattern] = list()

        # purge potentially dangerous/tricky characters
        bannedStrings.append(re.compile(r'\&|\%|\;|\=|\'|\"|\||\^|\~', re.IGNORECASE))

        # purge what might be directory traversal sequences
        bannedStrings.append(re.compile(r'\.{2,}', re.IGNORECASE))

        # purge various help flags
        bannedStrings.append(re.compile(r'(^|\s+)-h', re.IGNORECASE))
        bannedStrings.append(re.compile(r'(^|\s+)-\?', re.IGNORECASE))

        # purge various input flags
        bannedStrings.append(re.compile(r'(^|\s+)-pre', re.IGNORECASE))
        bannedStrings.append(re.compile(r'(^|\s+)-post', re.IGNORECASE))
        bannedStrings.append(re.compile(r'^\s*text', re.IGNORECASE))

        # purge user dictionary flag
        bannedStrings.append(re.compile(r'(^|\s+)-d', re.IGNORECASE))

        # purge version information flag
        bannedStrings.append(re.compile(r'(^|\s+)-v', re.IGNORECASE))

        # purge language flag
        bannedStrings.append(re.compile(r'(^|\s+)-lang(\s+\w+)?', re.IGNORECASE))

        # purge various output flags
        bannedStrings.append(re.compile(r'(^|\s+)-w', re.IGNORECASE))
        bannedStrings.append(re.compile(r'(^|\s+)-l((\[\w+\])|\w+)?', re.IGNORECASE))

        return bannedStrings

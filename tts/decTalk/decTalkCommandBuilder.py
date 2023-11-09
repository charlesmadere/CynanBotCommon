import re
from typing import List, Match, Optional, Pattern

try:
    import CynanBotCommon.utils as utils
    from CynanBotCommon.contentScanner.contentCode import ContentCode
    from CynanBotCommon.contentScanner.contentScannerInterface import \
        ContentScannerInterface
    from CynanBotCommon.emojiHelper.emojiHelperInterface import \
        EmojiHelperInterface
    from CynanBotCommon.timber.timberInterface import TimberInterface
    from CynanBotCommon.tts.ttsCheerDonation import TtsCheerDonation
    from CynanBotCommon.tts.ttsCommandBuilderInterface import \
        TtsCommandBuilderInterface
    from CynanBotCommon.tts.ttsDonation import TtsDonation
    from CynanBotCommon.tts.ttsDonationType import TtsDonationType
    from CynanBotCommon.tts.ttsEvent import TtsEvent
    from CynanBotCommon.tts.ttsSettingsRepositoryInterface import \
        TtsSettingsRepositoryInterface
    from CynanBotCommon.tts.ttsSubscriptionDonation import \
        TtsSubscriptionDonation
except:
    import utils
    from contentScanner.contentCode import ContentCode
    from contentScanner.contentScannerInterface import ContentScannerInterface
    from emojiHelper.emojiHelperInterface import EmojiHelperInterface
    from timber.timberInterface import TimberInterface
    from tts.ttsCheerDonation import TtsCheerDonation
    from tts.ttsCommandBuilderInterface import TtsCommandBuilderInterface
    from tts.ttsDonation import TtsDonation
    from tts.ttsDonationType import TtsDonationType
    from tts.ttsEvent import TtsEvent
    from tts.ttsSettingsRepositoryInterface import \
        TtsSettingsRepositoryInterface
    from tts.ttsSubscriptionDonation import TtsSubscriptionDonation


class DecTalkCommandBuilder(TtsCommandBuilderInterface):

    def __init__(
        self,
        contentScanner: ContentScannerInterface,
        emojiHelper: EmojiHelperInterface,
        timber: TimberInterface,
        ttsSettingsRepository: TtsSettingsRepositoryInterface,
        toneLowerVolume: str = '[:volume down 1]',
        toneHigherVolume: str =  '[:volume up 99]'
    ):
        if not isinstance(contentScanner, ContentScannerInterface):
            raise ValueError(f'contentScanner argument is malformed: \"{contentScanner}\"')
        elif not isinstance(emojiHelper, EmojiHelperInterface):
            raise ValueError(f'emojiHelper argument is malformed: \"{emojiHelper}\"')
        elif not isinstance(timber, TimberInterface):
            raise ValueError(f'timber argument is malformed: \"{timber}\"')
        elif not isinstance(ttsSettingsRepository, TtsSettingsRepositoryInterface):
            raise ValueError(f'ttsSettingsRepository argument is malformed: \"{ttsSettingsRepository}\"')
        elif not utils.isValidStr(toneLowerVolume):
            raise ValueError(f'toneLowerVolume argument is malformed: \"{toneLowerVolume}\"')
        elif not utils.isValidStr(toneHigherVolume):
            raise ValueError(f'toneHigherVolume argument is malformed: \"{toneHigherVolume}\"')

        self.__contentScanner: ContentScannerInterface = contentScanner
        self.__emojiHelper: EmojiHelperInterface = emojiHelper
        self.__timber: TimberInterface = timber
        self.__ttsSettingsRepository: TtsSettingsRepositoryInterface = ttsSettingsRepository
        self.__toneLowerVolume: str = toneLowerVolume
        self.__toneHigherVolume: str = toneHigherVolume

        self.__bannedStrings: List[Pattern] = self.__buildBannedStrings()
        self.__cheerStrings: List[Pattern] = self.__buildCheerStrings()
        self.__toneRegEx: Pattern = re.compile(r'\[\:(dial|tone).*?\]', re.IGNORECASE)
        self.__whiteSpaceRegEx: Pattern = re.compile(r'\s{2,}', re.IGNORECASE)

    async def buildAndCleanEvent(self, event: Optional[TtsEvent]) -> Optional[str]:
        if event is None:
            return None
        if not isinstance(event, TtsEvent):
            raise ValueError(f'event argument is malformed: \"{event}\"')

        prefix = await self.__processDonationPrefix(event)
        message = event.getMessage()

        if utils.isValidStr(message):
            message = await self.buildAndCleanMessage(message)

        if utils.isValidStr(prefix) and utils.isValidStr(message):
            return f'{prefix} {message}'
        elif utils.isValidStr(prefix):
            return prefix
        elif utils.isValidStr(message):
            return message
        else:
            return None

    async def buildAndCleanMessage(self, message: Optional[str]) -> Optional[str]:
        if not utils.isValidStr(message):
            return None

        contentCode = await self.__contentScanner.scan(message)

        if contentCode is not ContentCode.OK:
            self.__timber.log('DecTalkCommandBuilder', f'TTS command \"{message}\" returned a bad content code: \"{contentCode}\"')
            return None

        for cheerString in self.__cheerStrings:
            message = cheerString.sub(' ', message)

            if not utils.isValidStr(message):
                return None

        if not utils.isValidStr(message):
            return None

        for bannedString in self.__bannedStrings:
            message = bannedString.sub('', message)

            if not utils.isValidStr(message):
                return None

        if not utils.isValidStr(message):
            return None

        maxMessageSize = await self.__ttsSettingsRepository.getMaximumMessageSize()

        if len(message) > maxMessageSize:
            self.__timber.log('DecTalkCommandBuilder', f'Chopping down TTS command \"{message}\" as it is too long (len={len(message)}) ({maxMessageSize=}) ({message})')
            message = message[:maxMessageSize].strip()

        message = await self.__emojiHelper.replaceEmojisWithHumanNames(message)

        # remove extranneous whitespace
        message = self.__whiteSpaceRegEx.sub(' ', message).strip()

        if not utils.isValidStr(message):
            return None

        # DECTalk requires Windows-1252 encoding
        return message.encode().decode('windows-1252')

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

        # purge error inline command
        bannedStrings.append(re.compile(r'\[\:erro.*\]', re.IGNORECASE))

        # purge log inline command
        bannedStrings.append(re.compile(r'\[\:log.*\]', re.IGNORECASE))

        # purge sync mode inline command
        bannedStrings.append(re.compile(r'\[\:mode.*\]', re.IGNORECASE))

        # purge dial inline command
        bannedStrings.append(re.compile(r'\[\:dial.*\]', re.IGNORECASE))

        # purge period pause inline command
        bannedStrings.append(re.compile(r'\[\:peri.*\]', re.IGNORECASE))
        bannedStrings.append(re.compile(r'\[\:pp.*\]', re.IGNORECASE))

        # purge pitch inline command
        bannedStrings.append(re.compile(r'\[\:pitch.*\]', re.IGNORECASE))

        # purge play inline command
        bannedStrings.append(re.compile(r'\[\:play.*\]', re.IGNORECASE))

        # purge sync inline command
        bannedStrings.append(re.compile(r'\[\:sync.*\]', re.IGNORECASE))

        # purge tone inline command
        bannedStrings.append(re.compile(r'\[\:tone.*\]', re.IGNORECASE))

        # purge volume inline command
        bannedStrings.append(re.compile(r'\[\:volu.*\]', re.IGNORECASE))

        return bannedStrings

    def __buildCheerStrings(self) -> List[Pattern]:
        cheerStrings: List[Pattern] = list()

        # purge "cheer100"
        cheerStrings.append(re.compile(r'(^|\s+)cheer\d+(\s+|$)', re.IGNORECASE))

        # purge "uni100"
        cheerStrings.append(re.compile(r'(^|\s+)uni\d+(\s+|$)', re.IGNORECASE))

        return cheerStrings

    async def __insertVolumeInlineCommands(self, message: str) -> str:
        if not utils.isValidStr(message):
            raise ValueError(f'message argument is malformed: \"{message}\"')

        firstSearch = True
        startPosition = 0
        searchResult: Optional[Match] = None

        # input: "hello world [:dial 423]"
        # output: "hello world [:volume 1] [:dial 423] [:volume 9]"

        while firstSearch or searchResult is not None:
            if firstSearch:
                firstSearch = False

            searchResult = self.__toneRegEx.search(message, startPosition)

            if searchResult is None:
                continue

            beginning = message[:searchResult.start()]
            middle = message[searchResult.start():searchResult.end()]
            end = message[searchResult.end():]
            message = f'{beginning}{self.__toneLowerVolume}{middle}{self.__toneHigherVolume}{end}'
            startPosition = searchResult.start() + len(self.__toneLowerVolume) + len(middle) + len(self.__toneHigherVolume)

        return message

    async def __processCheerDonationPrefix(
        self,
        event: TtsEvent,
        donation: TtsCheerDonation
    ) -> Optional[str]:
        if not isinstance(event, TtsEvent):
            raise ValueError(f'event argument is malformed: \"{event}\"')
        elif not isinstance(donation, TtsCheerDonation):
            raise ValueError(f'donation argument is malformed: \"{donation}\"')
        elif donation.getType() is not TtsDonationType.CHEER:
            raise ValueError(f'TtsDonationType is not {TtsDonationType.CHEER}: \"{donation.getType()}\"')

        return f'{event.getUserName()} cheered {donation.getBits()}!'

    async def __processDonationPrefix(self, event: TtsEvent) -> Optional[str]:
        if not isinstance(event, TtsEvent):
            raise ValueError(f'event argument is malformed: \"{event}\"')

        donation: Optional[TtsDonation] = event.getDonation()

        if donation is None:
            return None

        donationType = donation.getType()

        if donationType is TtsDonationType.CHEER:
            return await self.__processCheerDonationPrefix(
                event = event,
                donation = donation
            )
        elif donationType is TtsDonationType.SUBSCRIPTION:
            return await self.__processSusbcriptionDonationPrefix(
                event = event,
                donation = donation
            )
        else:
            raise RuntimeError(f'donationType is unknown: \"{donationType}\"')

    async def __processSusbcriptionDonationPrefix(
        self,
        event: TtsEvent,
        donation: TtsSubscriptionDonation
    ) -> Optional[str]:
        if not isinstance(event, TtsEvent):
            raise ValueError(f'event argument is malformed: \"{event}\"')
        elif not isinstance(donation, TtsSubscriptionDonation):
            raise ValueError(f'donation argument is malformed: \"{donation}\"')
        elif donation.getType() is not TtsDonationType.SUBSCRIPTION:
            raise ValueError(f'TtsDonationType is not {TtsDonationType.SUBSCRIPTION}: \"{donation.getType()}\"')

        # I don't think it makes sense for a subscription to be anonymous, and also not a gift?

        if donation.isAnonymous() and donation.isGift():
            return f'anonymous gifted a sub!'
        elif donation.isGift():
            return f'{event.getUserName()} gifted a sub!'
        else:
            return f'{event.getUserName()} subscribed!'

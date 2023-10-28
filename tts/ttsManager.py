import re
from typing import List, Optional, Pattern

try:
    import CynanBotCommon.utils as utils
    from CynanBotCommon.contentScanner.contentCode import ContentCode
    from CynanBotCommon.contentScanner.contentScannerInterface import \
        ContentScannerInterface
    from CynanBotCommon.systemCommandHelper.systemCommandHelperInterface import \
        SystemCommandHelperInterface
    from CynanBotCommon.timber.timberInterface import TimberInterface
    from CynanBotCommon.tts.ttsManagerInterface import TtsManagerInterface
    from CynanBotCommon.tts.ttsSettingsRepositoryInterface import \
        TtsSettingsRepositoryInterface
    from CynanBotCommon.users.userInterface import UserInterface
except:
    import utils
    from contentScanner.contentCode import ContentCode
    from contentScanner.contentScannerInterface import ContentScannerInterface
    from systemCommandHelper.systemCommandHelperInterface import \
        SystemCommandHelperInterface
    from timber.timberInterface import TimberInterface
    from tts.ttsManagerInterface import TtsManagerInterface
    from tts.ttsSettingsRepositoryInterface import \
        TtsSettingsRepositoryInterface

    from users.userInterface import UserInterface


class TtsManager(TtsManagerInterface):

    def __init__(
        self,
        contentScanner: ContentScannerInterface,
        systemCommandHelper: SystemCommandHelperInterface,
        timber: TimberInterface,
        ttsSettingsRepository: TtsSettingsRepositoryInterface
    ):
        if not isinstance(contentScanner, ContentScannerInterface):
            raise ValueError(f'contentScanner argument is malformed: \"{contentScanner}\"')
        elif not isinstance(systemCommandHelper, SystemCommandHelperInterface):
            raise ValueError(f'systemCommandHelper argument is malformed: \"{systemCommandHelper}\"')
        elif not isinstance(timber, TimberInterface):
            raise ValueError(f'timber argument is malformed: \"{timber}\"')
        elif not isinstance(ttsSettingsRepository, TtsSettingsRepositoryInterface):
            raise ValueError(f'ttsSettingsRepository argument is malformed: \"{ttsSettingsRepository}\"')

        self.__contentScanner: ContentScannerInterface = contentScanner
        self.__systemCommandHelper: SystemCommandHelperInterface = systemCommandHelper
        self.__timber: TimberInterface = timber
        self.__ttsSettingsRepository: TtsSettingsRepositoryInterface = ttsSettingsRepository

        self.__bannedPhrases: List[Pattern] = self.__buildBannedPhrases()

    def __buildBannedPhrases(self) -> List[Pattern]:
        bannedPhrases: List[Pattern] = list()

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

    async def executeTts(self, user: UserInterface, message: str):
        if not isinstance(user, UserInterface):
            raise ValueError(f'user argument is malformed: \"{user}\"')
        elif not utils.isValidStr(message):
            raise ValueError(f'message argument is malformed: \"{message}\"')

        if not user.isTtsEnabled():
            self.__timber.log('TtsManager', f'User \"{user.getHandle()}\" does not have TTS enabled')
            return

        if not await self.__ttsSettingsRepository.isTtsEnabled():
            return

        command = await self.__processMessageIntoCommand(
            user = user,
            message = message
        )

        if not utils.isValidStr(command):
            self.__timber.log('TtsManager', f'Failed to parse TTS message for \"{user.getHandle()}\" into a valid command: \"{message}\"')
            return

        self.__timber.log('TtsManager', f'Executing TTS message for \"{user.getHandle()}\": \"{command}\"...')
        await self.__systemCommandHelper.executeCommand(command)

    async def __processMessageIntoCommand(
        self,
        user: UserInterface,
        message: str
    ) -> Optional[str]:
        if not isinstance(user, UserInterface):
            raise ValueError(f'user argument is malformed: \"{user}\"')
        elif not utils.isValidStr(message):
            raise ValueError(f'message argument is malformed: \"{message}\"')

        maxMessageSize = await self.__ttsSettingsRepository.getMaximumMessageSize()

        if len(message) > maxMessageSize:
            self.__timber.log('TtsManager', f'Chopping down TTS message for \"{user.getHandle()}\" as it is too long (len={len(message)}) ({maxMessageSize=}) ({message})')
            message = message[:maxMessageSize]

        contentCode = await self.__contentScanner.scan(message)

        if contentCode is not ContentCode.OK:
            self.__timber.log('TtsManager', f'TTS message for \"{user.getHandle()}\" returned a bad content code: \"{contentCode}\"')
            return None

        for bannedPhrase in self.__bannedPhrases:
            message = bannedPhrase.sub('', message)

            if not utils.isValidStr(message):
                return None

        if not utils.isValidStr(message):
            return None

        return f'say {message}'

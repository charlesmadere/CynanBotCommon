import asyncio
import queue
import re
import traceback
from queue import SimpleQueue
from typing import List, Optional, Pattern

try:
    import CynanBotCommon.utils as utils
    from CynanBotCommon.backgroundTaskHelper import BackgroundTaskHelper
    from CynanBotCommon.contentScanner.contentCode import ContentCode
    from CynanBotCommon.contentScanner.contentScannerInterface import \
        ContentScannerInterface
    from CynanBotCommon.systemCommandHelper.systemCommandHelperInterface import \
        SystemCommandHelperInterface
    from CynanBotCommon.timber.timberInterface import TimberInterface
    from CynanBotCommon.tts.ttsEvent import TtsEvent
    from CynanBotCommon.tts.ttsManagerInterface import TtsManagerInterface
    from CynanBotCommon.tts.ttsSettingsRepositoryInterface import \
        TtsSettingsRepositoryInterface
except:
    import utils
    from backgroundTaskHelper import BackgroundTaskHelper
    from contentScanner.contentCode import ContentCode
    from contentScanner.contentScannerInterface import ContentScannerInterface
    from systemCommandHelper.systemCommandHelperInterface import \
        SystemCommandHelperInterface
    from timber.timberInterface import TimberInterface
    from tts.ttsEvent import TtsEvent
    from tts.ttsManagerInterface import TtsManagerInterface
    from tts.ttsSettingsRepositoryInterface import \
        TtsSettingsRepositoryInterface


class TtsManager(TtsManagerInterface):

    def __init__(
        self,
        backgroundTaskHelper: BackgroundTaskHelper,
        contentScanner: ContentScannerInterface,
        systemCommandHelper: SystemCommandHelperInterface,
        timber: TimberInterface,
        ttsSettingsRepository: TtsSettingsRepositoryInterface,
        queueSleepTimeSeconds: float = 3,
        queueTimeoutSeconds: int = 3,
        pathToDecTalk: str = '../dectalk/speak_us.exe'
    ):
        if not isinstance(backgroundTaskHelper, BackgroundTaskHelper):
            raise ValueError(f'backgroundTaskHelper argument is malformed: \"{backgroundTaskHelper}\"')
        elif not isinstance(contentScanner, ContentScannerInterface):
            raise ValueError(f'contentScanner argument is malformed: \"{contentScanner}\"')
        elif not isinstance(systemCommandHelper, SystemCommandHelperInterface):
            raise ValueError(f'systemCommandHelper argument is malformed: \"{systemCommandHelper}\"')
        elif not isinstance(timber, TimberInterface):
            raise ValueError(f'timber argument is malformed: \"{timber}\"')
        elif not isinstance(ttsSettingsRepository, TtsSettingsRepositoryInterface):
            raise ValueError(f'ttsSettingsRepository argument is malformed: \"{ttsSettingsRepository}\"')
        elif not utils.isValidNum(queueSleepTimeSeconds):
            raise ValueError(f'queueSleepTimeSeconds argument is malformed: \"{queueSleepTimeSeconds}\"')
        elif queueSleepTimeSeconds < 1 or queueSleepTimeSeconds > 15:
            raise ValueError(f'queueSleepTimeSeconds argument is out of bounds: {queueSleepTimeSeconds}')
        elif not utils.isValidNum(queueTimeoutSeconds):
            raise ValueError(f'queueTimeoutSeconds argument is malformed: \"{queueTimeoutSeconds}\"')
        elif queueTimeoutSeconds < 1 or queueTimeoutSeconds > 5:
            raise ValueError(f'queueTimeoutSeconds argument is out of bounds: {queueTimeoutSeconds}')
        elif not utils.isValidStr(pathToDecTalk):
            raise ValueError(f'pathToDecTalk argument is malformed: \"{pathToDecTalk}\"')

        self.__backgroundTaskHelper: BackgroundTaskHelper = backgroundTaskHelper
        self.__contentScanner: ContentScannerInterface = contentScanner
        self.__systemCommandHelper: SystemCommandHelperInterface = systemCommandHelper
        self.__timber: TimberInterface = timber
        self.__ttsSettingsRepository: TtsSettingsRepositoryInterface = ttsSettingsRepository
        self.__queueSleepTimeSeconds: float = queueSleepTimeSeconds
        self.__queueTimeoutSeconds: int = queueTimeoutSeconds
        self.__pathToDecTalk: str = pathToDecTalk

        self.__isStarted: bool = False
        self.__bannedPhrases: List[Pattern] = self.__buildBannedPhrases()
        self.__eventQueue: SimpleQueue[TtsEvent] = SimpleQueue()

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

    async def __processMessageIntoCommand(
        self,
        message: Optional[str],
        twitchChannel: str
    ) -> Optional[str]:
        if not utils.isValidStr(message):
            return None
        elif not utils.isValidStr(twitchChannel):
            raise ValueError(f'twitchChannel argument is malformed: \"{twitchChannel}\"')

        maxMessageSize = await self.__ttsSettingsRepository.getMaximumMessageSize()

        if len(message) > maxMessageSize:
            self.__timber.log('TtsManager', f'Chopping down TTS message in \"{twitchChannel}\" as it is too long (len={len(message)}) ({maxMessageSize=}) ({message})')
            message = message[:maxMessageSize]

        contentCode = await self.__contentScanner.scan(message)

        if contentCode is not ContentCode.OK:
            self.__timber.log('TtsManager', f'TTS message in \"{twitchChannel}\" returned a bad content code: \"{contentCode}\"')
            return None

        for bannedPhrase in self.__bannedPhrases:
            message = bannedPhrase.sub('', message)

            if not utils.isValidStr(message):
                return None

        if not utils.isValidStr(message):
            return None

        return f'{self.__pathToDecTalk} say {message}'

    async def __processTtsEvent(self, event: TtsEvent):
        if not isinstance(event, TtsEvent):
            raise ValueError(f'event argument is malformed: \"{event}\"')

        if not await self.__ttsSettingsRepository.isTtsEnabled():
            return

        command = await self.__processMessageIntoCommand(
            message = event.getMessage(),
            twitchChannel = event.getTwitchChannel()
        )

        if not utils.isValidStr(command):
            self.__timber.log('TtsManager', f'Failed to parse TTS message in \"{event.getTwitchChannel()}\" into a valid command: \"{event.getMessage()}\"')
            return

        self.__timber.log('TtsManager', f'Executing TTS message in \"{event.getTwitchChannel()}\": \"{command}\"...')
        await self.__systemCommandHelper.executeCommand(command)

    def start(self):
        if self.__isStarted:
            self.__timber.log('TtsManager', 'Not starting TtsManager as it has already been started')
            return

        self.__isStarted = True
        self.__timber.log('TtsManager', 'Starting TtsManager...')

        self.__backgroundTaskHelper.createTask(self.__startEventLoop())

    async def __startEventLoop(self):
        while True:
            events: List[TtsEvent] = list()

            try:
                while not self.__eventQueue.empty():
                    events.append(self.__eventQueue.get_nowait())
            except queue.Empty as e:
                self.__timber.log('TtsManager', f'Encountered queue.Empty when building up events list (queue size: {self.__eventQueue.qsize()}) (events size: {len(events)}): {e}', e, traceback.format_exc())

            for event in events:
                try:
                    await self.__processTtsEvent(event)
                except Exception as e:
                    self.__timber.log('TtsManager', f'Encountered unknown Exception when looping through events (queue size: {self.__eventQueue.qsize()}) (event=\"{event}\"): {e}', e, traceback.format_exc())

            await asyncio.sleep(self.__queueSleepTimeSeconds)

    def submitTtsEvent(self, event: TtsEvent):
        if not isinstance(event, TtsEvent):
            raise ValueError(f'event argument is malformed: \"{event}\"')

        try:
            self.__eventQueue.put(event, block = True, timeout = self.__queueTimeoutSeconds)
        except queue.Full as e:
            self.__timber.log('TtsManager', f'Encountered queue.Full when submitting a new event ({event}) into the event queue (queue size: {self.__eventQueue.qsize()}): {e}', e, traceback.format_exc())

import asyncio
import os
import queue
import traceback
import uuid
from queue import SimpleQueue
from typing import Optional

import aiofiles
import aiofiles.os
import aiofiles.ospath

try:
    import CynanBotCommon.utils as utils
    from CynanBotCommon.backgroundTaskHelper import BackgroundTaskHelper
    from CynanBotCommon.systemCommandHelper.systemCommandHelperInterface import \
        SystemCommandHelperInterface
    from CynanBotCommon.timber.timberInterface import TimberInterface
    from CynanBotCommon.tts.decTalkCommandBuilder import DecTalkCommandBuilder
    from CynanBotCommon.tts.ttsCommandBuilderInterface import \
        TtsCommandBuilderInterface
    from CynanBotCommon.tts.ttsEvent import TtsEvent
    from CynanBotCommon.tts.ttsManagerInterface import TtsManagerInterface
    from CynanBotCommon.tts.ttsSettingsRepositoryInterface import \
        TtsSettingsRepositoryInterface
except:
    import utils
    from backgroundTaskHelper import BackgroundTaskHelper
    from systemCommandHelper.systemCommandHelperInterface import \
        SystemCommandHelperInterface
    from timber.timberInterface import TimberInterface
    from tts.decTalkCommandBuilder import DecTalkCommandBuilder
    from tts.ttsCommandBuilderInterface import TtsCommandBuilderInterface
    from tts.ttsEvent import TtsEvent
    from tts.ttsManagerInterface import TtsManagerInterface
    from tts.ttsSettingsRepositoryInterface import \
        TtsSettingsRepositoryInterface


class DecTalkManager(TtsManagerInterface):

    def __init__(
        self,
        backgroundTaskHelper: BackgroundTaskHelper,
        ttsCommandBuilder: DecTalkCommandBuilder,
        systemCommandHelper: SystemCommandHelperInterface,
        timber: TimberInterface,
        ttsSettingsRepository: TtsSettingsRepositoryInterface,
        queueSleepTimeSeconds: float = 3,
        queueTimeoutSeconds: float = 3,
        pathToDecTalk: str = '../dectalk/say.exe',
        tempFileDirectory: str = 'temp'
    ):
        if not isinstance(backgroundTaskHelper, BackgroundTaskHelper):
            raise ValueError(f'backgroundTaskHelper argument is malformed: \"{backgroundTaskHelper}\"')
        elif not isinstance(ttsCommandBuilder, DecTalkCommandBuilder):
            raise ValueError(f'ttsCommandBuilder argument is malformed: \"{ttsCommandBuilder}\"')
        elif not isinstance(systemCommandHelper, SystemCommandHelperInterface):
            raise ValueError(f'systemCommandHelper argument is malformed: \"{systemCommandHelper}\"')
        elif not isinstance(timber, TimberInterface):
            raise ValueError(f'timber argument is malformed: \"{timber}\"')
        elif not isinstance(ttsSettingsRepository, TtsSettingsRepositoryInterface):
            raise ValueError(f'ttsSettingsRepository argument is malformed: \"{ttsSettingsRepository}\"')
        elif not utils.isValidInt(queueSleepTimeSeconds):
            raise ValueError(f'queueSleepTimeSeconds argument is malformed: \"{queueSleepTimeSeconds}\"')
        elif queueSleepTimeSeconds < 1 or queueSleepTimeSeconds > 10:
            raise ValueError(f'queueSleepTimeSeconds argument is out of bounds: {queueSleepTimeSeconds}')
        elif not utils.isValidInt(queueTimeoutSeconds):
            raise ValueError(f'queueTimeoutSeconds argument is malformed: \"{queueTimeoutSeconds}\"')
        elif queueTimeoutSeconds < 1 or queueTimeoutSeconds > 3:
            raise ValueError(f'queueTimeoutSeconds argument is out of bounds: {queueTimeoutSeconds}')
        elif not utils.isValidStr(pathToDecTalk):
            raise ValueError(f'pathToDecTalk argument is malformed: \"{pathToDecTalk}\"')
        elif not utils.isValidStr(tempFileDirectory):
            raise ValueError(f'tempFileDirectory argument is malformed: \"{tempFileDirectory}\"')

        self.__backgroundTaskHelper: BackgroundTaskHelper = backgroundTaskHelper
        self.__systemCommandHelper: SystemCommandHelperInterface = systemCommandHelper
        self.__timber: TimberInterface = timber
        self.__ttsCommandBuilder: TtsCommandBuilderInterface = ttsCommandBuilder
        self.__ttsSettingsRepository: TtsSettingsRepositoryInterface = ttsSettingsRepository
        self.__queueSleepTimeSeconds: float = queueSleepTimeSeconds
        self.__queueTimeoutSeconds: float = queueTimeoutSeconds
        self.__pathToDecTalk: str = utils.cleanPath(pathToDecTalk)
        self.__tempFileDirectory: str = utils.cleanPath(tempFileDirectory)

        self.__isStarted: bool = False
        self.__eventQueue: SimpleQueue[TtsEvent] = SimpleQueue()

    async def __createTtsTempFile(self, command: str) -> Optional[str]:
        if not utils.isValidStr(command):
            raise ValueError(f'command argument is malformed: \"{command}\"')

        if not await aiofiles.ospath.exists(self.__tempFileDirectory):
            await aiofiles.os.makedirs(self.__tempFileDirectory)

        fileName = utils.cleanPath(f'{self.__tempFileDirectory}/dectalk_{uuid.uuid4()}.txt')

        # DECTalk requires Windows-1252 encoding
        async with aiofiles.open(
            file = fileName,
            mode = 'w',
            encoding = 'windows-1252',
            loop = self.__backgroundTaskHelper.getEventLoop()
        ) as file:
            await file.write(command)

        return fileName

    async def __deleteTtsTempFile(self, fileName: Optional[str]):
        if not utils.isValidStr(fileName):
            return
        elif not await aiofiles.ospath.exists(fileName):
            return

        try:
            os.remove(fileName)
        except Exception as e:
            self.__timber.log('DecTalkManager', f'Unable to delete temporary TTS file (\"{fileName}\"): {e}', e, traceback.format_exc())

    async def __processTtsEvent(self, event: TtsEvent):
        if not isinstance(event, TtsEvent):
            raise ValueError(f'event argument is malformed: \"{event}\"')

        if not await self.__ttsSettingsRepository.isTtsEnabled():
            return

        command = await self.__ttsCommandBuilder.buildAndCleanEvent(event)

        if not utils.isValidStr(command):
            self.__timber.log('DecTalkManager', f'Failed to parse TTS message in \"{event.getTwitchChannel()}\" into a valid command: \"{event}\"')
            return

        fileName = await self.__createTtsTempFile(command)

        if not utils.isValidStr(fileName):
            self.__timber.log('DecTalkManager', f'Failed to write TTS message in \"{event.getTwitchChannel()}\" to temporary file ({command=})')
            return

        self.__timber.log('DecTalkManager', f'Executing TTS message in \"{event.getTwitchChannel()}\"...')

        await self.__systemCommandHelper.executeCommand(
            command = f'{self.__pathToDecTalk} -pre \"[:phone on]\" < \"{fileName}\"',
            timeoutSeconds = await self.__ttsSettingsRepository.getTtsTimeoutSeconds()
        )

        await self.__deleteTtsTempFile(fileName)

    def start(self):
        if self.__isStarted:
            self.__timber.log('DecTalkManager', 'Not starting DecTalkManager as it has already been started')
            return

        self.__isStarted = True
        self.__timber.log('DecTalkManager', 'Starting DecTalkManager...')

        self.__backgroundTaskHelper.createTask(self.__startEventLoop())

    async def __startEventLoop(self):
        while True:
            event: Optional[TtsEvent] = None

            if not self.__eventQueue.empty():
                try:
                    event = self.__eventQueue.get_nowait()
                except queue.Empty as e:
                    self.__timber.log('DecTalkManager', f'Encountered queue.Empty when grabbing event from queue (queue size: {self.__eventQueue.qsize()}): {e}', e, traceback.format_exc())

            if event is None:
                await asyncio.sleep(self.__queueSleepTimeSeconds)
                continue

            try:
                await self.__processTtsEvent(event)
            except Exception as e:
                self.__timber.log('DecTalkManager', f'Encountered unexpected exception when processing TTS event (event: {event}) (queue size: {self.__eventQueue.qsize()}): {e}', e, traceback.format_exc())

            await asyncio.sleep(await self.__ttsSettingsRepository.getTtsDelayBetweenSeconds())

    def submitTtsEvent(self, event: TtsEvent):
        if not isinstance(event, TtsEvent):
            raise ValueError(f'event argument is malformed: \"{event}\"')

        try:
            self.__eventQueue.put(event, block = True, timeout = self.__queueTimeoutSeconds)
        except queue.Full as e:
            self.__timber.log('DecTalkManager', f'Encountered queue.Full when submitting a new event ({event}) into the event queue (queue size: {self.__eventQueue.qsize()}): {e}', e, traceback.format_exc())

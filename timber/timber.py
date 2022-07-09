import asyncio
import queue
from asyncio import AbstractEventLoop
from queue import SimpleQueue

import aiofiles
import aiofiles.os
import aiofiles.ospath

try:
    import CynanBotCommon.utils as utils
    from CynanBotCommon.timber.timberEntry import TimberEntry
except:
    import utils

    from timber.timberEntry import TimberEntry


class Timber():

    def __init__(
        self,
        eventLoop: AbstractEventLoop,
        alsoPrintToStandardOut: bool = True,
        sleepTimeSeconds: float = 5,
        timberRootDirectory: str = 'CynanBotCommon/timber'
    ):
        if eventLoop is None:
            raise ValueError(f'eventLoop argument is malformed: \"{eventLoop}\"')
        elif not utils.isValidBool(alsoPrintToStandardOut):
            raise ValueError(f'alsoPrintToStandardOut argument is malformed: \"{alsoPrintToStandardOut}\"')
        elif not utils.isValidNum(sleepTimeSeconds):
            raise ValueError(f'sleepTimeSeconds argument is malformed: \"{sleepTimeSeconds}\"')
        elif sleepTimeSeconds < 0.1 or sleepTimeSeconds > 60:
            raise ValueError(f'sleepTimeSeconds argument is out of bounds: {sleepTimeSeconds}')
        elif not utils.isValidStr(timberRootDirectory):
            raise ValueError(f'timberRootDirectory argument is malformed: \"{timberRootDirectory}\"')

        self.__alsoPrintToStandardOut: bool = alsoPrintToStandardOut
        self.__sleepTimeSeconds: float = sleepTimeSeconds
        self.__timberRootDirectory: str = timberRootDirectory

        self.__entryQueue: SimpleQueue[TimberEntry] = SimpleQueue()
        eventLoop.create_task(self.__startEventLoop())

    def __getLogStatement(
        self,
        ensureNewLine: bool,
        timberEntry: TimberEntry
    ) -> str:
        if not utils.isValidBool(ensureNewLine):
            raise ValueError(f'ensureNewLine argument is malformed: \"{ensureNewLine}\"')
        elif timberEntry is None:
            raise ValueError(f'timberEntry argument is malformed: \"{timberEntry}\"')

        logStatement = f'{timberEntry.getSimpleDateTime().getDateAndTimeStr()} — {timberEntry.getTag()} — {timberEntry.getMsg()}'
        logStatement = logStatement.strip()

        if ensureNewLine:
            logStatement = f'{logStatement}\n'

        return logStatement

    def log(self, tag: str, msg: str):
        if not utils.isValidStr(tag):
            raise ValueError(f'tag argument is malformed: \"{tag}\"')
        elif not utils.isValidStr(msg):
            raise ValueError(f'msg argument is malformed: \"{msg}\"')

        timberEntry = TimberEntry(tag, msg)
        self.__entryQueue.put(timberEntry)

    async def __log(self, timberEntry: TimberEntry):
        if timberEntry is None:
            raise ValueError(f'timberEntry argument is malformed: \"{timberEntry}\"')

        await self.__writeToLogFile(timberEntry)

        if self.__alsoPrintToStandardOut:
            print(self.__getLogStatement(False, timberEntry))

    async def __startEventLoop(self):
        while True:
            try:
                while not self.__entryQueue.empty():
                    timberEntry = self.__entryQueue.get_nowait()
                    await self.__log(timberEntry)
            except queue.Empty:
                pass

            await asyncio.sleep(self.__sleepTimeSeconds)

    async def __writeToLogFile(self, timberEntry: TimberEntry):
        if timberEntry is None:
            raise ValueError(f'timberEntry argument is malformed: \"{timberEntry}\"')

        sdt = timberEntry.getSimpleDateTime()
        timberDirectory = f'{self.__timberRootDirectory}/{sdt.getYearStr()}/{sdt.getMonthStr()}'
        timberFile = f'{timberDirectory}/{sdt.getDayStr()}.log'

        if not await aiofiles.ospath.exists(timberDirectory):
            await aiofiles.os.makedirs(timberDirectory)

        logStatement = self.__getLogStatement(True, timberEntry)

        async with aiofiles.open(timberFile, mode = 'a') as file:
            await file.write(logStatement)

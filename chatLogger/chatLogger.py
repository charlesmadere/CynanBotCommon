import asyncio
import queue
from asyncio import AbstractEventLoop
from queue import SimpleQueue

import aiofiles
import aiofiles.os
import aiofiles.ospath

try:
    import CynanBotCommon.utils as utils
    from CynanBotCommon.chatLogger.absChatMessage import AbsChatMessage
    from CynanBotCommon.chatLogger.chatEventType import ChatEventType
    from CynanBotCommon.chatLogger.chatMessage import ChatMessage
    from CynanBotCommon.chatLogger.raidMessage import RaidMessage
except:
    import utils

    from chatLogger.absChatMessage import AbsChatMessage
    from chatLogger.chatEventType import ChatEventType
    from chatLogger.chatMessage import ChatMessage
    from chatLogger.raidMessage import RaidMessage


class ChatLogger():

    def __init__(
        self,
        eventLoop: AbstractEventLoop,
        sleepTimeSeconds: float = 10,
        logRootDirectory: str = 'CynanBotCommon/chatLogger'
    ):
        if eventLoop is None:
            raise ValueError(f'eventLoop argument is malformed: \"{eventLoop}\"')
        elif not utils.isValidNum(sleepTimeSeconds):
            raise ValueError(f'sleepTimeSeconds argument is malformed: \"{sleepTimeSeconds}\"')
        elif sleepTimeSeconds < 1 or sleepTimeSeconds > 60:
            raise ValueError(f'sleepTimeSeconds argument is out of bounds: {sleepTimeSeconds}')
        elif not utils.isValidStr(logRootDirectory):
            raise ValueError(f'logRootDirectory argument is malformed: \"{logRootDirectory}\"')

        self.__sleepTimeSeconds: float = sleepTimeSeconds
        self.__logRootDirectory: str = logRootDirectory

        self.__messageQueue: SimpleQueue[AbsChatMessage] = SimpleQueue()
        eventLoop.create_task(self.__startMessageLoop())

    def __getLogStatement(self, message: AbsChatMessage) -> str:
        if message is None:
            raise ValueError(f'message argument is malformed: \"{message}\"')

        logStatement: str = f'{message.getSimpleDateTime().getDateAndTimeStr()} —'

        if message.getChatEventType() is ChatEventType.MESSAGE:
            chatMessage: ChatMessage = message
            logStatement = f'{logStatement} {chatMessage.getUserName()} ({chatMessage.getUserId()}) — {chatMessage.getMsg()}'
        elif message.getChatEventType() is ChatEventType.RAID:
            raidMessage: RaidMessage = message
            logStatement = f'{logStatement} Received raid from {raidMessage.getFromWho()} of {raidMessage.getRaidSizeStr()}!'
        else:
            raise RuntimeError(f'AbsChatMessage has unknown ChatEventType: \"{message.getChatEventType()}\"')

        return f'{logStatement.strip()}\n'

    def logMessage(self, msg: str, twitchChannel: str, userId: str, userName: str):
        if not utils.isValidStr(msg):
            raise ValueError(f'msg argument is malformed: \"{msg}\"')
        elif not utils.isValidStr(twitchChannel):
            raise ValueError(f'twitchChannel argument is malformed: \"{twitchChannel}\"')
        elif not utils.isValidStr(userId):
            raise ValueError(f'userId argument is malformed: \"{userId}\"')
        elif not utils.isValidStr(userName):
            raise ValueError(f'userName argument is malformed: \"{userName}\"')

        chatMessage: AbsChatMessage = ChatMessage(
            msg = msg,
            twitchChannel = twitchChannel,
            userId = userId,
            userName = userName
        )

        self.__messageQueue.put(chatMessage)

    def logRaid(self, raidSize: int, fromWho: str, twitchChannel: str):
        if not utils.isValidNum(raidSize):
            raise ValueError(f'raidSize argument is malformed: \"{raidSize}\"')
        elif raidSize < 0:
            raise ValueError(f'raidSize argument is out of bounds: {raidSize}')
        elif not utils.isValidStr(fromWho):
            raise ValueError(f'fromWho argument is malformed: \"{fromWho}\"')
        elif not utils.isValidStr(twitchChannel):
            raise ValueError(f'twitchChannel argument is malformed: \"{twitchChannel}\"')

        raidMessage: AbsChatMessage = RaidMessage(
            raidSize = raidSize,
            fromWho = fromWho,
            twitchChannel = twitchChannel
        )

        self.__messageQueue.put(raidMessage)

    async def __startMessageLoop(self):
        while True:
            try:
                while not self.__messageQueue.empty():
                    message = self.__messageQueue.get_nowait()
                    await self.__writeToLogFile(message)
            except queue.Empty:
                pass

            await asyncio.sleep(self.__sleepTimeSeconds)

    async def __writeToLogFile(self, message: AbsChatMessage):
        if message is None:
            raise ValueError(f'message argument is malformed: \"{message}\"')

        sdt = message.getSimpleDateTime()
        messageDirectory = f'{self.__logRootDirectory}/{message.getTwitchChannel()}/{sdt.getYearStr()}/{sdt.getMonthStr()}'
        messageFile = f'{messageDirectory}/{sdt.getDayStr()}.log'

        if not await aiofiles.ospath.exists(messageDirectory):
            await aiofiles.os.makedirs(messageDirectory)

        logStatement = self.__getLogStatement(message)

        async with aiofiles.open(messageFile, mode = 'a') as file:
            await file.write(logStatement)

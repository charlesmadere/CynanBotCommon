import asyncio
import queue
from asyncio import AbstractEventLoop
from queue import SimpleQueue

import aiofiles
import aiofiles.os
import aiofiles.ospath

try:
    import CynanBotCommon.utils as utils
    from CynanBotCommon.chatLogger.chatMessage import ChatMessage
except:
    import utils

    from chatLogger.chatMessage import ChatMessage


class ChatLogger():

    def __init__(
        self,
        eventLoop: AbstractEventLoop,
        sleepTimeSeconds: float = 15,
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

        self.__messageQueue: SimpleQueue[ChatMessage] = SimpleQueue()
        eventLoop.create_task(self.__startMessageLoop())

    def __getLogStatement(self, chatMessage: ChatMessage) -> str:
        if chatMessage is None:
            raise ValueError(f'chatMessage argument is malformed: \"{chatMessage}\"')

        logStatement = f'{chatMessage.getSimpleDateTime().getDateAndTimeStr()} — {chatMessage.getUserName()} ({chatMessage.getUserId()}) — {chatMessage.getMsg()}'
        logStatement = logStatement.strip()

        return f'{logStatement}\n'

    def log(self, twitchChannel: str, userId: str, userName: str, msg: str):
        if not utils.isValidStr(twitchChannel):
            raise ValueError(f'twitchChannel argument is malformed: \"{twitchChannel}\"')
        elif not utils.isValidStr(userId):
            raise ValueError(f'userId argument is malformed: \"{userId}\"')
        elif not utils.isValidStr(userName):
            raise ValueError(f'userName argument is malformed: \"{userName}\"')
        elif not utils.isValidStr(msg):
            raise ValueError(f'msg argument is malformed: \"{msg}\"')

        chatMessage = ChatMessage(twitchChannel, userId, userName, msg)
        self.__messageQueue.put(chatMessage)

    async def __startMessageLoop(self):
        while True:
            try:
                while not self.__messageQueue.empty():
                    chatMessage = self.__messageQueue.get_nowait()
                    await self.__writeToLogFile(chatMessage)
            except queue.Empty:
                pass

            await asyncio.sleep(self.__sleepTimeSeconds)

    async def __writeToLogFile(self, chatMessage: ChatMessage):
        if chatMessage is None:
            raise ValueError(f'chatMessage argument is malformed: \"{chatMessage}\"')

        sdt = chatMessage.getSimpleDateTime()
        messageDirectory = f'{self.__logRootDirectory}/{chatMessage.getTwitchChannel()}/{sdt.getYearStr()}/{sdt.getMonthStr()}'
        messageFile = f'{messageDirectory}/{sdt.getDayStr()}.log'

        if not await aiofiles.ospath.exists(messageDirectory):
            await aiofiles.os.makedirs(messageDirectory)

        logStatement = self.__getLogStatement(chatMessage)

        async with aiofiles.open(messageFile, mode = 'a') as file:
            await file.write(logStatement)

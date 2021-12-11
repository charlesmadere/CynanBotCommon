import asyncio
import json
from asyncio import AbstractEventLoop
from datetime import datetime, timedelta
from queue import SimpleQueue
from typing import Dict

import websockets

try:
    import CynanBotCommon.utils as utils
except:
    import utils


class WebsocketEvent():

    def __init__(
        self,
        eventData: Dict
    ):
        if not utils.hasItems(eventData):
            raise ValueError(f'eventData argument is malformed: \"{eventData}\"')

        self.__eventTime: datetime = datetime.utcnow()
        self.__eventData: Dict = eventData

    def getEventData(self) -> Dict:
        return self.__eventData

    def getEventDataAsJson(self) -> str:
        return json.dumps(self.__eventData)

    def getEventTime(self):
        return self.__eventTime


class WebsocketConnectionServer():

    def __init__(
        self,
        isDebugLoggingEnabled: bool = True,
        maxSendAttempts: int = 3,
        port: int = 8765,
        sleepTimeSeconds: int = 5,
        host: str = '0.0.0.0',
        timeToLive: timedelta = timedelta(minutes = 1)
    ):
        if not utils.isValidBool(isDebugLoggingEnabled):
            raise ValueError(f'isDebugLoggingEnabled argument is malformed: \"{isDebugLoggingEnabled}\"')
        elif not utils.isValidNum(maxSendAttempts):
            raise ValueError(f'maxSendAttempts argument is malformed: \"{maxSendAttempts}\"')
        elif maxSendAttempts < 1 or maxSendAttempts > 5:
            raise ValueError(f'maxSendAttempts argument is out of bounds: \"{maxSendAttempts}\"')
        elif not utils.isValidNum(port):
            raise ValueError(f'port argument is malformed: \"{port}\"')
        elif port <= 0:
            raise ValueError(f'port argument is out of bounds: \"{port}\"')
        elif not utils.isValidNum(sleepTimeSeconds):
            raise ValueError(f'sleepTimeSeconds argument is malformed: \"{sleepTimeSeconds}\"')
        elif sleepTimeSeconds < 3:
            raise ValueError(f'sleepTimeSeconds argument is too aggressive: \"{sleepTimeSeconds}\"')
        elif not utils.isValidStr(host):
            raise ValueError(f'host argument is malformed: \"{host}\"')
        elif timeToLive is None:
            raise ValueError(f'timeToLive argument is malformed: \"{timeToLive}\"')

        self.__isDebugLoggingEnabled: bool = isDebugLoggingEnabled
        self.__maxSendAttempts: int = maxSendAttempts
        self.__port: int = port
        self.__sleepTimeSeconds: int = sleepTimeSeconds
        self.__host: str = host
        self.__timeToLive: timedelta = timeToLive

        self.__isStarted: bool = False
        self.__eventQueue: SimpleQueue[WebsocketEvent] = SimpleQueue()

    async def sendEvent(
        self,
        twitchChannel: str,
        eventType: str,
        eventData: Dict
    ):
        if not utils.isValidStr(twitchChannel):
            raise ValueError(f'twitchChannel argument is malformed: \"{twitchChannel}\"')
        elif not utils.isValidStr(eventType):
            raise ValueError(f'eventType argument for twitchChannel \"{twitchChannel}\" is malformed: \"{eventType}\"')
        elif not utils.hasItems(eventData):
            raise ValueError(f'eventData argument for eventType \"{eventType}\" and twitchChannel \"{twitchChannel}\" is malformed: \"{eventData}\"')

        event = {
            'twitchChannel': twitchChannel,
            'eventType': eventType,
            'eventData': eventData
        }

        if not self.__isStarted:
            print(f'The websocket server has not yet been started, but attempted to add event to queue ({utils.getNowTimeText(includeSeconds = True)}):\n{event}')
            return

        if self.__isDebugLoggingEnabled:
            print(f'Adding event to queue (current size is {self.__eventQueue.qsize()}, new size will be {self.__eventQueue.qsize() + 1}) ({utils.getNowTimeText(includeSeconds = True)}):\n{event}')

        self.__eventQueue.put(WebsocketEvent(eventData = event))

    def start(self, eventLoop: AbstractEventLoop):
        if eventLoop is None:
            raise ValueError(f'eventLoop argument is malformed: \"{eventLoop}\"')

        if self.__isStarted:
            print(f'Not starting websocket server, as it has already been started ({utils.getNowTimeText(includeSeconds = True)})')
            return

        print(f'Starting websocket connection server... ({utils.getNowTimeText(includeSeconds = True)})')
        self.__isStarted = True
        eventLoop.create_task(self.__start())

    async def __start(self):
        while True:
            try:
                async with websockets.serve(
                    self.__websocketConnectionReceived,
                    host = self.__host,
                    port = self.__port
                ):
                    await asyncio.Future()
            except Exception as e:
                print(f'WebsocketConnectionServer encountered exception within `__start()`: {e}')

            asyncio.sleep(self.__sleepTimeSeconds)

    async def __websocketConnectionReceived(self, websocket, path):
        if self.__isDebugLoggingEnabled:
            print(f'Established websocket connection to: \"{path}\" (current queue size is {self.__eventQueue.qsize()})')

        while True:
            try:
                while not self.__eventQueue.empty():
                    event = self.__eventQueue.get(block = True, timeout = 3)
                    attempt = 0

                    if event.getEventTime() + self.__timeToLive >= datetime.utcnow():
                        eventJson = event.getEventDataAsJson()

                        while attempt < self.__maxSendAttempts:
                            attempt = attempt + 1

                            try:
                                await websocket.send(eventJson)
                                attempt = self.__maxSendAttempts
                            except Exception as e:
                                if self.__isDebugLoggingEnabled:
                                    print(f'WebsocketConnectionServer failed to send event on attempt {attempt} of {self.__maxSendAttempts} ({utils.getNowTimeText(includeSeconds = True)})\n{event.getEventData()}: {e}')
                                else:
                                    print(f'WebsocketConnectionServer failed to send event on attempt {attempt} of {self.__maxSendAttempts} ({utils.getNowTimeText(includeSeconds = True)}): {e}')

                                if attempt >= self.__maxSendAttempts:
                                    raise e

                        if self.__isDebugLoggingEnabled:
                            print(f'WebsocketConnectionServer sent event to \"{path}\": \"{event.getEventData()}\"')
                    elif self.__isDebugLoggingEnabled:
                        print(f'WebsocketConnectionServer discarded an event meant for \"{path}\": \"{event.getEventData()}\"')
            except Exception as e:
                print(f'WebsocketConnectionServer encountered exception within `__websocketConnectionReceived()`: {e}')

            await asyncio.sleep(self.__sleepTimeSeconds)

import asyncio
import json
from asyncio import AbstractEventLoop
from datetime import datetime, timedelta
from queue import SimpleQueue
from typing import Dict

import websockets

try:
    import CynanBotCommon.utils as utils
    from CynanBotCommon.websocketConnection.websocketEvent import \
        WebsocketEvent
except:
    import utils

    from websocketConnection.websocketEvent import WebsocketEvent


class WebsocketConnectionServer():

    def __init__(
        self,
        isDebugLoggingEnabled: bool = True,
        eventQueueBlockTimeoutSeconds: int = 3,
        port: int = 8765,
        sleepTimeSeconds: int = 5,
        host: str = '0.0.0.0',
        eventTimeToLive: timedelta = timedelta(seconds = 30)
    ):
        if not utils.isValidBool(isDebugLoggingEnabled):
            raise ValueError(f'isDebugLoggingEnabled argument is malformed: \"{isDebugLoggingEnabled}\"')
        elif not utils.isValidNum(eventQueueBlockTimeoutSeconds):
            raise ValueError(f'eventQueueBlockTimeoutSeconds argument is malformed: \"{eventQueueBlockTimeoutSeconds}\"')
        elif eventQueueBlockTimeoutSeconds < 1:
            raise ValueError(f'eventQueueBlockTimeoutSeconds is out of bounds: \"{eventQueueBlockTimeoutSeconds}\"')
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
        elif eventTimeToLive is None:
            raise ValueError(f'eventTimeToLive argument is malformed: \"{eventTimeToLive}\"')

        self.__isDebugLoggingEnabled: bool = isDebugLoggingEnabled
        self.__eventQueueBlockTimeoutSeconds: int = eventQueueBlockTimeoutSeconds
        self.__port: int = port
        self.__sleepTimeSeconds: int = sleepTimeSeconds
        self.__host: str = host
        self.__eventTimeToLive: timedelta = eventTimeToLive

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
        if self.__isDebugLoggingEnabled:
            print(f'WebsocketConnectionServer has entered `__start()` ({utils.getNowTimeText(includeSeconds = True)})')

        while True:
            try:
                async with websockets.serve(
                    self.__websocketConnectionReceived,
                    host = self.__host,
                    port = self.__port
                ) as websocket:
                    if self.__isDebugLoggingEnabled:
                        print(f'WebsocketConnectionServer is looping within `__start()` ({utils.getNowTimeText(includeSeconds = True)})')

                    await websocket.wait_closed()
            except Exception as e:
                print(f'WebsocketConnectionServer encountered exception within `__start()` ({utils.getNowTimeText(includeSeconds = True)}): {e}')

            if self.__isDebugLoggingEnabled:
                print(f'WebsocketConnectionServer is sleeping within `__start()` ({utils.getNowTimeText(includeSeconds = True)})')

            asyncio.sleep(self.__sleepTimeSeconds)

    async def __websocketConnectionReceived(self, websocket, path):
        if self.__isDebugLoggingEnabled:
            print(f'WebsocketConnectionServer is entering `__websocketConnectionReceived()` (path: \"{path}\") (queue size: {self.__eventQueue.qsize()}) ({utils.getNowTimeText(includeSeconds = True)})')

        while websocket.open:
            while not self.__eventQueue.empty():
                event = self.__eventQueue.get(
                    block = True,
                    timeout = self.__eventQueueBlockTimeoutSeconds
                )

                if event.getEventTime() + self.__eventTimeToLive >= datetime.utcnow():
                    eventJson = json.dumps(event.getEventData())
                    await websocket.send(eventJson)

                    if self.__isDebugLoggingEnabled:
                        print(f'WebsocketConnectionServer sent event to \"{path}\" ({utils.getNowTimeText(includeSeconds = True)}):\n{event.getEventData()}')
                    else:
                        print(f'WebsocketConnectionServer sent event to \"{path}\" ({utils.getNowTimeText(includeSeconds = True)})')
                else:
                    if self.__isDebugLoggingEnabled:
                        print(f'WebsocketConnectionServer discarded an event meant for \"{path}\" ({utils.getNowTimeText(includeSeconds = True)})\n{event.getEventData()}')
                    else:
                        print(f'WebsocketConnectionServer discarded an event meant for \"{path}\" ({utils.getNowTimeText(includeSeconds = True)})')

            await asyncio.sleep(self.__sleepTimeSeconds)

        if self.__isDebugLoggingEnabled:
            print(f'WebsocketConnectionServer is exiting `__websocketConnectionReceived()` ({utils.getNowTimeText(includeSeconds = True)})')

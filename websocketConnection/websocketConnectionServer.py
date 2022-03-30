import asyncio
import json
from asyncio import AbstractEventLoop
from datetime import datetime, timedelta, timezone
from queue import SimpleQueue
from typing import Dict

import websockets

try:
    import CynanBotCommon.utils as utils
    from CynanBotCommon.timber.timber import Timber
    from CynanBotCommon.websocketConnection.websocketEvent import \
        WebsocketEvent
except:
    import utils
    from timber.timber import Timber

    from websocketConnection.websocketEvent import WebsocketEvent


class WebsocketConnectionServer():

    def __init__(
        self,
        timber: Timber,
        isDebugLoggingEnabled: bool = False,
        eventQueueBlockTimeoutSeconds: int = 3,
        port: int = 8765,
        sleepTimeSeconds: int = 5,
        host: str = '0.0.0.0',
        eventTimeToLive: timedelta = timedelta(seconds = 30)
    ):
        if timber is None:
            raise ValueError(f'timber argument is malformed: \"{timber}\"')
        elif not utils.isValidBool(isDebugLoggingEnabled):
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

        self.__timber: Timber = timber
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
            self.__timber.log('WebsocketConnectionServer', f'Server has not yet been started, but attempted to add event to queue: {event}')
            return

        if self.__isDebugLoggingEnabled:
            currentSize = self.__eventQueue.qsize()
            self.__timber.log('WebsocketConnectionServer', f'Adding event to queue (current size is {currentSize}, new size will be {currentSize + 1}): {event}')

        self.__eventQueue.put(WebsocketEvent(eventData = event))

    def start(self, eventLoop: AbstractEventLoop):
        if eventLoop is None:
            raise ValueError(f'eventLoop argument is malformed: \"{eventLoop}\"')

        if self.__isStarted:
            self.__timber.log('WebsocketConnectionServer', 'Not starting server as it has already been started')
            return

        self.__timber.log('WebsocketConnectionServer', 'Starting server...')
        self.__isStarted = True
        eventLoop.create_task(self.__start())

    async def __start(self):
        if self.__isDebugLoggingEnabled:
            self.__timber.log('WebsocketConnectionServer', f'Entered `__start()` (queue size: {self.__eventQueue.qsize()})')

        while True:
            try:
                async with websockets.serve(
                    self.__websocketConnectionReceived,
                    host = self.__host,
                    port = self.__port
                ) as websocket:
                    if self.__isDebugLoggingEnabled:
                        self.__timber.log('WebsocketConnectionServer', f'Looping within `__start()`')

                    await websocket.wait_closed()
            except Exception as e:
                self.__timber.log('WebsocketConnectionServer', f'Encountered exception within `__start()`: {e}')

                if str(e) == 'Event loop is closed':
                    # this annoying code provides us an escape from this infinite loop when using
                    # CTRL+C at the terminal to stop the bot
                    self.__timber.log('WebsocketConnectionServer', f'Breaking from `__start()` loop')
                    break

            if self.__isDebugLoggingEnabled:
                self.__timber.log('WebsocketConnectionServer', f'Sleeping within `__start()`')

            asyncio.sleep(self.__sleepTimeSeconds)

    async def __websocketConnectionReceived(self, websocket, path):
        if self.__isDebugLoggingEnabled:
            self.__timber.log('WebsocketConnectionServer', f'Entered `__websocketConnectionReceived()` (path: \"{path}\") (queue size: {self.__eventQueue.qsize()})')

        while websocket.open:
            while not self.__eventQueue.empty():
                event = self.__eventQueue.get(
                    block = True,
                    timeout = self.__eventQueueBlockTimeoutSeconds
                )

                if event.getEventTime() + self.__eventTimeToLive >= datetime.now(timezone.utc):
                    eventJson = json.dumps(event.getEventData())
                    await websocket.send(eventJson)

                    if self.__isDebugLoggingEnabled:
                        self.__timber.log('WebsocketConnectionServer', f'Sent event to \"{path}\": {event.getEventData()}')
                    else:
                        self.__timber.log('WebsocketConnectionServer', f'Sent event to \"{path}\"')
                else:
                    if self.__isDebugLoggingEnabled:
                        self.__timber.log('WebsocketConnectionServer', f'Discarded an event meant for \"{path}\": {event.getEventData()}')
                    else:
                        self.__timber.log('WebsocketConnectionServer', f'Discarded an event meant for \"{path}\"')

            await asyncio.sleep(self.__sleepTimeSeconds)

        if self.__isDebugLoggingEnabled:
            self.__timber.log('WebsocketConnectionServer', f'Exiting `__websocketConnectionReceived()`')

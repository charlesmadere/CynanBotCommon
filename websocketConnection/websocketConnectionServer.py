import asyncio
import json
import queue
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
        eventLoop: AbstractEventLoop,
        timber: Timber,
        isDebugLoggingEnabled: bool = False,
        sleepTimeSeconds: float = 5,
        port: int = 8765,
        host: str = '0.0.0.0',
        eventTimeToLive: timedelta = timedelta(seconds = 30)
    ):
        if eventLoop is None:
            raise ValueError(f'eventLoop argument is malformed: \"{eventLoop}\"')
        elif timber is None:
            raise ValueError(f'timber argument is malformed: \"{timber}\"')
        elif not utils.isValidBool(isDebugLoggingEnabled):
            raise ValueError(f'isDebugLoggingEnabled argument is malformed: \"{isDebugLoggingEnabled}\"')
        elif not utils.isValidNum(sleepTimeSeconds):
            raise ValueError(f'sleepTimeSeconds argument is malformed: \"{sleepTimeSeconds}\"')
        elif sleepTimeSeconds < 3:
            raise ValueError(f'sleepTimeSeconds argument is too aggressive: {sleepTimeSeconds}')
        elif not utils.isValidNum(port):
            raise ValueError(f'port argument is malformed: \"{port}\"')
        elif port <= 100:
            raise ValueError(f'port argument is out of bounds: \"{port}\"')
        elif not utils.isValidStr(host):
            raise ValueError(f'host argument is malformed: \"{host}\"')
        elif eventTimeToLive is None:
            raise ValueError(f'eventTimeToLive argument is malformed: \"{eventTimeToLive}\"')

        self.__timber: Timber = timber
        self.__isDebugLoggingEnabled: bool = isDebugLoggingEnabled
        self.__port: int = port
        self.__sleepTimeSeconds: int = sleepTimeSeconds
        self.__host: str = host
        self.__eventTimeToLive: timedelta = eventTimeToLive

        self.__eventQueue: SimpleQueue[WebsocketEvent] = SimpleQueue()
        eventLoop.create_task(self.__startEventLoop())

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

        if self.__isDebugLoggingEnabled:
            currentSize = self.__eventQueue.qsize()
            self.__timber.log('WebsocketConnectionServer', f'Adding event to queue (current size is {currentSize}, new size will be {currentSize + 1}): {event}')

        self.__eventQueue.put(WebsocketEvent(eventData = event))

    async def __startEventLoop(self):
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

            await asyncio.sleep(self.__sleepTimeSeconds)

    async def __websocketConnectionReceived(self, websocket, path):
        if self.__isDebugLoggingEnabled:
            self.__timber.log('WebsocketConnectionServer', f'Entered `__websocketConnectionReceived()` (path: \"{path}\") (queue size: {self.__eventQueue.qsize()})')

        while websocket.open:
            while not self.__eventQueue.empty():
                try:
                    event = self.__eventQueue.get(block = False)

                    if event.getEventTime() + self.__eventTimeToLive >= datetime.now(timezone.utc):
                        eventJson = json.dumps(event.getEventData(), sort_keys = True)
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
                except queue.Empty as e:
                    self.__timber.log('WebsocketConnectionServer', f'Encountered queue.Empty error when looping through events (queue size: {self.__eventQueue.qsize()}): {e}')

            await asyncio.sleep(self.__sleepTimeSeconds)

        if self.__isDebugLoggingEnabled:
            self.__timber.log('WebsocketConnectionServer', f'Exiting `__websocketConnectionReceived()`')

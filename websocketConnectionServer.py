import asyncio
import json
from asyncio import AbstractEventLoop
from queue import SimpleQueue
from typing import Dict

import websockets

try:
    import CynanBotCommon.utils as utils
except:
    import utils


class WebsocketConnectionServer():

    def __init__(
        self,
        isDebugLoggingEnabled: bool = True,
        port: int = 8765,
        sleepTimeSeconds: int = 5,
        host: str = '127.0.0.1'
    ):
        if not utils.isValidBool(isDebugLoggingEnabled):
            raise ValueError(f'isDebugLoggingEnabled argument is malformed: \"{isDebugLoggingEnabled}\"')
        elif not utils.isValidNum(port):
            raise ValueError(f'port argument is malformed: \"{port}\"')
        elif not utils.isValidNum(sleepTimeSeconds):
            raise ValueError(f'sleepTimeSeconds argument is malformed: \"{sleepTimeSeconds}\"')
        elif sleepTimeSeconds < 3:
            raise ValueError(f'sleepTimeSeconds argument is too aggressive: \"{sleepTimeSeconds}\"')
        elif not utils.isValidStr(host):
            raise ValueError(f'host argument is malformed: \"{host}\"')

        self.__isDebugLoggingEnabled: bool = isDebugLoggingEnabled
        self.__port: int = port
        self.__sleepTimeSeconds: int = sleepTimeSeconds
        self.__host: str = host

        self.__isStarted: bool = False
        self.__eventQueue: SimpleQueue[str] = SimpleQueue()

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
        elif eventData is None:
            raise ValueError(f'eventData argument for eventType \"{eventType}\" and twitchChannel \"{twitchChannel}\" is malformed: \"{eventData}\"')

        event = {
            'twitchChannel': twitchChannel,
            'eventType': eventType,
            'eventData': eventData
        }

        eventStr = json.dumps(event)

        if not self.__isStarted:
            print(f'The websocket server has not yet been started, but attempted to add event to queue ({utils.getNowTimeText(includeSeconds = True)}): {eventStr}')
            return

        if self.__isDebugLoggingEnabled:
            print(f'Adding event to queue (current size is {len(self.__eventQueue)}, new size will be {len(self.__eventQueue) + 1}) ({utils.getNowTimeText(includeSeconds = True)}): {eventStr}')

        self.__eventQueue.put(eventStr)

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
        async with websockets.serve(
            self.__websocketConnectionReceived,
            host = self.__host,
            port = self.__port
        ):
            await asyncio.Future()

    async def __websocketConnectionReceived(self, websocket, path):
        print(f'Established websocket connection to: {path}')

        while True:
            try:
                while not self.__eventQueue.empty():
                    event = self.__eventQueue.get()
                    await websocket.send(event)

                    if self.__isDebugLoggingEnabled:
                        print(f'Sent event over websocket connection to {path}: \"{event}\"')
            except websockets.ConnectionClosed as e:
                print(f'Websocket connection to {path} closed: {e}')
                break

            await asyncio.sleep(self.__sleepTimeSeconds)

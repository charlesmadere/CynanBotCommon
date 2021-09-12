import asyncio
from enum import Enum, auto
from queue import SimpleQueue

import websockets

try:
    import CynanBotCommon.utils as utils
except:
    import utils


class SoundEvent(Enum):

    BASS = auto()
    DRUM = auto()
    WHISTLE = auto()

    def toStr(self) -> str:
        if self is SoundEvent.BASS:
            return 'bass'
        elif self is SoundEvent.DRUM:
            return 'drum'
        elif self is SoundEvent.WHISTLE:
            return 'whistle'
        else:
            raise ValueError(f'unknown SoundEvent: \"{self}\"')


class SoundEventsHelper():

    def __init__(
        self,
        port: int = 8765,
        sleepTimeSeconds: int = 5,
        host: str = '127.0.0.1'
    ):
        if not utils.isValidNum(port):
            raise ValueError(f'port argument is malformed: \"{port}\"')
        elif not utils.isValidNum(sleepTimeSeconds):
            raise ValueError(f'sleepTimeSeconds argument is malformed: \"{sleepTimeSeconds}\"')
        elif sleepTimeSeconds < 3:
            raise ValueError(f'sleepTimeSeconds argument is too aggressive: \"{sleepTimeSeconds}\"')
        elif not utils.isValidStr(host):
            raise ValueError(f'host argument is malformed: \"{host}\"')

        self.__port: int = port
        self.__sleepTimeSeconds: int = sleepTimeSeconds
        self.__host: str = host

        self.__isWebsocketServerStarted: bool = False
        self.__soundEventQueue: SimpleQueue[SoundEvent] = SimpleQueue()

    async def sendEvent(self, event: SoundEvent):
        if event is None:
            raise ValueError(f'event argument is malformed: \"{event}\"')

        if not self.__isWebsocketServerStarted:
            print(f'The websocket server has not yet been started, but attempted to send SoundEvent: \"{event}\" ({utils.getNowTimeText(includeSeconds = True)})')
            return

        self.__soundEventQueue.put(event)

    def startWebsocketServer(self, eventLoop):
        if eventLoop is None:
            raise ValueError(f'eventLoop argument is malformed: \"{eventLoop}\"')

        if self.__isWebsocketServerStarted:
            print(f'Not starting websocket server, as it has already been started ({utils.getNowTimeText(includeSeconds = True)})')
            return

        print(f'Starting websocket server... ({utils.getNowTimeText(includeSeconds = True)})')
        self.__isWebsocketServerStarted = True
        eventLoop.create_task(self.__startWebsocketServer())

    async def __startWebsocketServer(self):
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
                while not self.__soundEventQueue.empty():
                    soundEvent = self.__soundEventQueue.get()
                    await websocket.send(soundEvent.toStr())
                    print(f'Sent msgs')
            except websockets.ConnectionClosed as e:
                print(f'Websocket connection closed: {e}')
                break

            await asyncio.sleep(self.__sleepTimeSeconds)

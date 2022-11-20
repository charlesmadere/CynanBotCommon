from enum import Enum, auto

try:
    import CynanBotCommon.utils as utils
except:
    import utils


class NetworkClientType(Enum):

    AIOHTTP = auto()
    REQUESTS = auto()

    @classmethod
    def fromStr(cls, text: str):
        if not utils.isValidStr(text):
            raise ValueError(f'text argument is malformed: \"{text}\"')

        text = text.lower()

        if text == 'aiohttp':
            return NetworkClientType.AIOHTTP
        elif text == 'requests':
            return NetworkClientType.REQUESTS
        else:
            raise RuntimeError(f'unknown NetworkClientType: \"{text}\"')

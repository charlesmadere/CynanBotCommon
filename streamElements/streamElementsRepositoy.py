import json
import locale
import os
from asyncio import TimeoutError
from datetime import datetime, timedelta, timezone
from typing import Dict, List

import aiofile
import aiohttp

try:
    import CynanBotCommon.utils as utils
    from CynanBotCommon.timber.timber import Timber
except:
    import utils
    from timber.timber import Timber


class StreamElementsRepository():

    def __init__(
        self,
        clientSession: aiohttp.ClientSession,
        timber: Timber,
        streamElementsApiUrl: str = 'https://api.streamelements.com/kappa/v2',
        streamElementsRepositoryFile: str = 'CynanBotCommon/streamElements/streamElementsRepository.json'
    ):
        if clientSession is None:
            raise ValueError(f'clientSession argument is malformed: \"{clientSession}\"')
        elif timber is None:
            raise ValueError(f'timber argument is malformed: \"{timber}\"')
        elif not utils.isValidUrl(streamElementsApiUrl):
            raise ValueError(f'streamElementsApiUrl argument is malformed: \"{streamElementsApiUrl}\"')
        elif not utils.isValidStr(streamElementsRepositoryFile):
            raise ValueError(f'streamElementsRepositoryFile argument is malformed: \"{streamElementsRepositoryFile}\"')

        self.__clientSession: aiohttp.ClientSession = clientSession
        self.__timber: Timber = timber
        self.__streamElementsApiUrl: str = streamElementsApiUrl
        self.__streamElementsRepositoryFile: str = streamElementsRepositoryFile



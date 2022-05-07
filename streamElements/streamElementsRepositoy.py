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
    from CynanBotCommon.streamElements.streamElementsExceptions import (
        NoBearerTokenException, NoChannelGuuidException,
        StreamElementsNetworkException)
    from CynanBotCommon.streamElements.userPointsResult import UserPointsResult
    from CynanBotCommon.timber.timber import Timber
except:
    import utils
    from timber.timber import Timber

    from streamElements.streamElementsExceptions import (
        NoBearerTokenException, NoChannelGuuidException,
        StreamElementsNetworkException)
    from streamElements.userPointsResult import UserPointsResult


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

    async def __getChannelGuuid(self, twitchChannel: str) -> str:
        if not utils.isValidStr(twitchChannel):
            raise ValueError(f'twitchChannel argument is malformed: \"{twitchChannel}\"')

        twitchChannelJson = await self.__readJsonForTwitchChannel(twitchChannel)
        if twitchChannelJson is None:
            return None

        channelGuuid = twitchChannelJson.get('channelGuuid')
        if not utils.isValidStr(channelGuuid):
            raise ValueError(f'\"channelGuuid\" value for \"{twitchChannel}\" in StreamElements repository file ({self.__streamElementsRepositoryFile}) is malformed: \"{channelGuuid}\"')

        return channelGuuid

    async def getUserPoints(self, twitchChannel: str, userName: str) -> UserPointsResult:
        if not utils.isValidStr(twitchChannel):
            raise ValueError(f'twitchChannel argument is malformed: \"{twitchChannel}\"')
        elif not utils.isValidStr(userName):
            raise ValueError(f'userName argument is malformed: \"{userName}\"')

        channelGuuid = await self.__getChannelGuuid(twitchChannel)
        if not utils.isValidStr(channelGuuid):
            self.__timber.log('StreamElementsRepository', f'Can\'t perform getUserPoints as twitchChannel \"{twitchChannel}\" has no Channel GUUID: \"{channelGuuid}\"')
            raise NoChannelGuuidException(f'Can\'t perform getUserPoints as twitchChannel \"{twitchChannel}\" has no Channel GUUID: \"{channelGuuid}\"')

        bearerToken = await self.__requireBearerToken()

        response = None
        try:
            response = await self.__clientSession.get(
                url = f'{self.__streamElementsApiUrl}/points/{twitchChannel}/{userName}'
            )
        except (aiohttp.ClientError, TimeoutError) as e:
            self.__timber.log('StreamElementsRepository', f'Encountered network error for \"{twitchChannel}\" when trying to fetch user points for \"{userName}\": {e}')
            raise StreamElementsNetworkException(f'Encountered network error for \"{twitchChannel}\" when trying to fetch user points for \"{userName}\": {e}')

        # TODO
        return None

    async def __readAllJson(self) -> Dict[str, object]:
        if not os.path.exists(self.__streamElementsRepositoryFile):
            raise FileNotFoundError(f'StreamElements repository file not found: \"{self.__streamElementsRepositoryFile}\"')

        async with aiofile.async_open(self.__streamElementsRepositoryFile, 'r') as file:
            data = await file.read()
            jsonContents = json.loads(data)

        if jsonContents is None:
            raise IOError(f'Error reading from StreamElements repository file: \"{self.__streamElementsRepositoryFile}\"')
        elif len(jsonContents) == 0:
            raise ValueError(f'JSON contents of StreamElements repository file \"{self.__streamElementsRepositoryFile}\" is empty')

        return jsonContents

    async def __readJsonForTwitchChannel(self, twitchChannel: str) -> Dict[str, object]:
        if not utils.isValidStr(twitchChannel):
            raise ValueError(f'twitchChannel argument is malformed: \"{twitchChannel}\"')

        jsonContents = await self.__readAllJson()
        twitchChannelsJson: Dict[str, object] = jsonContents.get('twitchChannels')
        if not utils.hasItems(twitchChannelsJson):
            raise ValueError(f'\"twitchChannels\" JSON contents of StreamElements repository file \"{self.__streamElementsRepositoryFile}\" is missing/empty')

        twitchChannel = twitchChannel.lower()

        for key in twitchChannelsJson:
            if key.lower() == twitchChannel:
                return twitchChannelsJson[key]

        return None

    async def __requireBearerToken(self) -> str:
        jsonContents = await self.__readAllJson()
        bearerToken = jsonContents.get('bearerToken')

        if not utils.isValidStr(bearerToken):
            raise NoBearerTokenException(f'StreamElements \"bearerToken\" in \"{self.__streamElementsRepositoryFile}\" is missing or malformed: \"{bearerToken}\"')

        return bearerToken

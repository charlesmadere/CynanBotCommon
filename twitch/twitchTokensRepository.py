import json
import locale
from asyncio import TimeoutError
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Set

import aiofiles
import aiofiles.ospath
import aiohttp

try:
    import CynanBotCommon.utils as utils
    from CynanBotCommon.networkClientProvider import NetworkClientProvider
    from CynanBotCommon.timber.timber import Timber
    from CynanBotCommon.twitch.twitchAccessTokenMissingException import \
        TwitchAccessTokenMissingException
    from CynanBotCommon.twitch.twitchExpiresInMissingException import \
        TwitchExpiresInMissingException
    from CynanBotCommon.twitch.twitchJsonException import TwitchJsonException
    from CynanBotCommon.twitch.twitchNetworkException import \
        TwitchNetworkException
    from CynanBotCommon.twitch.twitchRefreshTokenMissingException import \
        TwitchRefreshTokenMissingException
except:
    import utils
    from networkClientProvider import NetworkClientProvider
    from timber.timber import Timber

    from twitch.twitchAccessTokenMissingException import \
        TwitchAccessTokenMissingException
    from twitch.twitchExpiresInMissingException import \
        TwitchExpiresInMissingException
    from twitch.twitchJsonException import TwitchJsonException
    from twitch.twitchNetworkException import TwitchNetworkException
    from twitch.twitchRefreshTokenMissingException import \
        TwitchRefreshTokenMissingException


class TwitchTokensRepository():

    def __init__(
        self,
        networkClientProvider: NetworkClientProvider,
        timber: Timber,
        oauth2TokenUrl: str = 'https://id.twitch.tv/oauth2/token',
        oauth2ValidateUrl: str = 'https://id.twitch.tv/oauth2/validate',
        twitchTokensFile: str = 'CynanBotCommon/twitch/twitchTokensRepository.json',
        tokensExpirationBuffer: timedelta = timedelta(minutes = 30)
    ):
        if networkClientProvider is None:
            raise ValueError(f'networkClientProvider argument is malformed: \"{networkClientProvider}\"')
        elif timber is None:
            raise ValueError(f'timber argument is malformed: \"{timber}\"')
        elif not utils.isValidUrl(oauth2TokenUrl):
            raise ValueError(f'oauth2TokenUrl argument is malformed: \"{oauth2TokenUrl}\"')
        elif not utils.isValidUrl(oauth2ValidateUrl):
            raise ValueError(f'oauth2ValidateUrl argument is malformed: \"{oauth2ValidateUrl}\"')
        elif not utils.isValidStr(twitchTokensFile):
            raise ValueError(f'twitchTokensFile argument is malformed: \"{twitchTokensFile}\"')
        elif tokensExpirationBuffer is None:
            raise ValueError(f'tokensExpirationBuffer argument is malformed: \"{tokensExpirationBuffer}\"')

        self.__networkClientProvider: NetworkClientProvider = networkClientProvider
        self.__timber: Timber = timber
        self.__oauth2TokenUrl: str = oauth2TokenUrl
        self.__oauth2ValidateUrl: str = oauth2ValidateUrl
        self.__twitchTokensFile: str = twitchTokensFile
        self.__tokensExpirationBuffer: timedelta = tokensExpirationBuffer

        self.__jsonCache: Dict[str, Any] = None
        self.__tokenExpirations: Dict[str, datetime] = dict()

    async def clearCaches(self):
        self.__jsonCache = None
        self.__timber.log('TwitchTokensRepository', f'Caches cleared')

    async def getAccessToken(self, twitchHandle: str) -> str:
        if not utils.isValidStr(twitchHandle):
            raise ValueError(f'twitchHandle argument is malformed: \"{twitchHandle}\"')

        jsonContents = await self.__readJsonForTwitchHandle(twitchHandle)
        return utils.getStrFromDict(jsonContents, 'accessToken', fallback = '')

    async def getExpiringTwitchHandles(self) -> List[str]:
        if not utils.hasItems(self.__tokenExpirations):
            return None

        expiringTwitchHandles: Set[str] = set()
        nowDateTime = datetime.now(timezone.utc)

        for twitchHandle, expirationDateTime in self.__tokenExpirations.items():
            if expirationDateTime is None or nowDateTime + self.__tokensExpirationBuffer >= expirationDateTime:
                expiringTwitchHandles.add(twitchHandle.lower())

        if await self.__isDynamicAdditionOfNewPubSubUsersEnabled():
            twitchHandlesJson = await self.__readAllTwitchHandleJson()

            for key in twitchHandlesJson:
                if key.lower() not in self.__tokenExpirations:
                    expiringTwitchHandles.add(key.lower())
                    self.__timber.log('TwitchTokensRepository', f'Discovered new PubSub user: \"{key}\"!')

        return list(expiringTwitchHandles)

    async def getRefreshToken(self, twitchHandle: str) -> str:
        if not utils.isValidStr(twitchHandle):
            raise ValueError(f'twitchHandle argument is malformed: \"{twitchHandle}\"')

        jsonContents = await self.__readJsonForTwitchHandle(twitchHandle)
        return utils.getStrFromDict(jsonContents, 'refreshToken', fallback = '')

    async def __isDebugLoggingEnabled(self) -> bool:
        jsonContents = await self.__readAllJson()
        return utils.getBoolFromDict(jsonContents, 'debugLoggingEnabled', fallback = False)

    async def __isDynamicAdditionOfNewPubSubUsersEnabled(self) -> bool:
        jsonContents = await self.__readAllJson()
        return utils.getBoolFromDict(jsonContents, 'dynamicAdditionOfNewPubSubUsers', fallback = True)

    async def __readAllJson(self) -> Dict[str, Any]:
        if self.__jsonCache is not None:
            return self.__jsonCache

        if not await aiofiles.ospath.exists(self.__twitchTokensFile):
            raise FileNotFoundError(f'Twitch tokens file not found: \"{self.__twitchTokensFile}\"')

        async with aiofiles.open(self.__twitchTokensFile, mode = 'r') as file:
            data = await file.read()
            jsonContents = json.loads(data)

        if jsonContents is None:
            raise IOError(f'Error reading from Twitch tokens file: \"{self.__twitchTokensFile}\"')
        elif len(jsonContents) == 0:
            raise ValueError(f'JSON contents of Twitch tokens file \"{self.__twitchTokensFile}\" is empty')

        self.__jsonCache = jsonContents
        return jsonContents

    async def __readAllTwitchHandleJson(self) -> Dict[str, Any]:
        jsonContents = await self.__readAllJson()
        twitchHandlesJson: Dict[str, Any] = jsonContents.get('twitchHandles')

        if not utils.hasItems(twitchHandlesJson):
            raise ValueError(f'\"twitchHandles\" JSON contents of Twitch tokens file \"{self.__twitchTokensFile}\" is missing/empty')

        return twitchHandlesJson

    async def __readJsonForTwitchHandle(self, twitchHandle: str) -> Dict[str, Any]:
        if not utils.isValidStr(twitchHandle):
            raise ValueError(f'twitchHandle argument is malformed: \"{twitchHandle}\"')

        twitchHandlesJson = await self.__readAllTwitchHandleJson()
        twitchHandle = twitchHandle.lower()

        for key in twitchHandlesJson:
            if key.lower() == twitchHandle:
                return twitchHandlesJson[key]

        # Return an empty dictionary if the given user isn't found in the Twitch tokens file. This
        # is a good bit easier to handle than throwing an exception, or something else like that.
        return dict()

    async def __refreshTokens(
        self,
        twitchClientId: str,
        twitchClientSecret: str,
        twitchHandle: str
    ):
        if not utils.isValidStr(twitchClientId):
            raise ValueError(f'twitchClientId argument is malformed: \"{twitchClientId}\"')
        elif not utils.isValidStr(twitchClientSecret):
            raise ValueError(f'twitchClientSecret argument is malformed: \"{twitchClientSecret}\"')
        elif not utils.isValidStr(twitchHandle):
            raise ValueError(f'twitchHandle argument is malformed: \"{twitchHandle}\"')

        twitchHandle = twitchHandle.lower()
        self.__timber.log('TwitchTokensRepository', f'Refreshing Twitch tokens for \"{twitchHandle}\"...')
        clientSession = await self.__networkClientProvider.get()

        try:
            response = await clientSession.post(
                url = self.__oauth2TokenUrl,
                params = {
                        'client_id': twitchClientId,
                        'client_secret': twitchClientSecret,
                        'grant_type': 'refresh_token',
                        'refresh_token': await self.requireRefreshToken(twitchHandle)
                }
            )
        except (aiohttp.ClientError, TimeoutError) as e:
            self.__timber.log('TwitchTokensRepository', f'Encountered network error when requesting new Twitch tokens for \"{twitchHandle}\": {e}')
            raise TwitchNetworkException(f'Encountered network error when requesting new Twitch tokens for \"{twitchHandle}\": {e}')

        if response.status != 200:
            self.__timber.log('TwitchTokensRepository', f'Encountered non-200 HTTP status code when requesting new Twitch tokens for \"{twitchHandle}\": {response.status}')
            raise TwitchNetworkException(f'Encountered non-200 HTTP status code when requesting new Twitch tokens for \"{twitchHandle}\": {response.status}')

        jsonResponse: Dict[str, Any] = await response.json()
        response.close()

        if not utils.hasItems(jsonResponse):
            self.__timber.log('TwitchTokensRepository', f'Received malformed JSON response when refreshing Twitch tokens for \"{twitchHandle}\": {jsonResponse}')
            raise TwitchJsonException(f'Received malformed JSON response when refreshing Twitch tokens for \"{twitchHandle}\": {jsonResponse}')

        accessToken = utils.getStrFromDict(jsonResponse, 'access_token', fallback = '')
        refreshToken = utils.getStrFromDict(jsonResponse, 'refresh_token', fallback = '')
        expiresInSeconds = utils.getIntFromDict(jsonResponse, 'expires_in', fallback = -1)

        if not utils.isValidStr(accessToken):
            self.__timber.log('TwitchTokensRepository', f'Received malformed \"access_token\" ({accessToken}) when refreshing Twitch tokens for \"{twitchHandle}\": {jsonResponse}')
            raise TwitchAccessTokenMissingException(f'Received malformed \"access_token\" ({accessToken}) when refreshing Twitch tokens for \"{twitchHandle}\": {jsonResponse}')
        elif not utils.isValidStr(refreshToken):
            self.__timber.log('TwitchTokensRepository', f'Received malformed \"refresh_token\" ({refreshToken}) when refreshing Twitch tokens for \"{twitchHandle}\": {jsonResponse}')
            raise TwitchRefreshTokenMissingException(f'Received malformed \"refresh_token\" ({refreshToken}) when refreshing Twitch tokens for \"{twitchHandle}\": {jsonResponse}')
        elif not utils.isValidNum(expiresInSeconds):
            self.__timber.log('TwitchTokensRepository', f'Received malformed \"expires_in\" ({expiresInSeconds}) when refreshing Twitch tokens for \"{twitchHandle}\": {jsonResponse}')
            raise TwitchExpiresInMissingException(f'Received malformed \"expires_in\" ({expiresInSeconds}) when refreshing Twitch tokens for \"{twitchHandle}\": {jsonResponse}')

        if await self.__isDebugLoggingEnabled():
            self.__timber.log('TwitchTokensRepository', f'JSON response for \"{twitchHandle}\" Twitch tokens refresh: {jsonResponse}')

        jsonContents = await self.__readAllJson()
        jsonContents['twitchHandles'][twitchHandle] = {
            'accessToken': accessToken,
            'refreshToken': refreshToken
        }

        jsonString: str = ''
        async with aiofiles.open(self.__twitchTokensFile, mode = 'w') as file:
            jsonString = json.dumps(jsonContents, indent = 4, sort_keys = True)
            await file.write(jsonString)

        # be sure to clear caches, as JSON file contents have now been updated
        await self.clearCaches()

        if await self.__isDebugLoggingEnabled():
            self.__timber.log('TwitchTokensRepository', f'{self.__twitchTokensFile} contents: {jsonString}')

        await self.__saveUserTokenExpirationTime(
            twitchHandle = twitchHandle,
            expiresInSeconds = expiresInSeconds
        )

    async def requireAccessToken(self, twitchHandle: str) -> str:
        if not utils.isValidStr(twitchHandle):
            raise ValueError(f'twitchHandle argument is malformed: \"{twitchHandle}\"')

        accessToken = await self.getAccessToken(twitchHandle)
        if not utils.isValidStr(accessToken):
            raise ValueError(f'\"accessToken\" value for \"{twitchHandle}\" in \"{self.__twitchTokensFile}\" is malformed: \"{accessToken}\"')

        return accessToken

    async def requireRefreshToken(self, twitchHandle: str) -> str:
        if not utils.isValidStr(twitchHandle):
            raise ValueError(f'twitchHandle argument is malformed: \"{twitchHandle}\"')

        refreshToken = await self.getRefreshToken(twitchHandle)
        if not utils.isValidStr(refreshToken):
            raise ValueError(f'\"refreshToken\" value for \"{twitchHandle}\" in \"{self.__twitchTokensFile}\" is malformed: \"{refreshToken}\"')

        return refreshToken

    async def __saveUserTokenExpirationTime(self, twitchHandle: str, expiresInSeconds: int):
        if not utils.isValidStr(twitchHandle):
            raise ValueError(f'twitchHandle argument is malformed: \"{twitchHandle}\"')
        elif not utils.isValidNum(expiresInSeconds):
            raise ValueError(f'expiresInSeconds argument is malformed: \"{expiresInSeconds}\"')
        elif expiresInSeconds <= 0:
            raise ValueError(f'expiresInSeconds can\'t be <= 0: {expiresInSeconds}')

        twitchHandle = twitchHandle.lower()
        nowDateTime = datetime.now(timezone.utc)
        expiresInTimeDelta = timedelta(seconds = expiresInSeconds)
        expirationTime = nowDateTime + expiresInTimeDelta
        self.__tokenExpirations[twitchHandle] = expirationTime

        expiresInSecondsStr = locale.format_string("%d", expiresInSeconds, grouping = True)
        self.__timber.log('TwitchTokensRepository', f'Set Twitch tokens for \"{twitchHandle}\" (expiration is in {expiresInSecondsStr} seconds, at {expirationTime})')

        if await self.__isDebugLoggingEnabled():
            self.__timber.log('TwitchTokensRepository', f'tokenExpirations contents: {self.__tokenExpirations}')

    async def validateAndRefreshAccessToken(
        self,
        twitchClientId: str,
        twitchClientSecret: str,
        twitchHandle: str
    ):
        if not utils.isValidStr(twitchClientId):
            raise ValueError(f'twitchClientId argument is malformed: \"{twitchClientId}\"')
        elif not utils.isValidStr(twitchClientSecret):
            raise ValueError(f'twitchClientSecret argument is malformed: \"{twitchClientSecret}\"')
        elif not utils.isValidStr(twitchHandle):
            raise ValueError(f'twitchHandle argument is malformed: \"{twitchHandle}\"')

        twitchHandle = twitchHandle.lower()
        self.__timber.log('TwitchTokensRepository', f'Validating Twitch access token for \"{twitchHandle}\"...')
        clientSession = await self.__networkClientProvider.get()

        try:
            response = await clientSession.get(
                url = self.__oauth2ValidateUrl,
                headers = {
                    'Authorization': f'OAuth {await self.requireAccessToken(twitchHandle)}'
                }
            )
        except (aiohttp.ClientError, TimeoutError) as e:
            self.__timber.log('TwitchTokensRepository', f'Encountered network error when validating Twitch access token for \"{twitchHandle}\": {e}')
            raise TwitchNetworkException(f'Encountered network error when validating Twitch access token for \"{twitchHandle}\": {e}')

        responseStatus: int = response.status
        jsonResponse: Dict[str, Any] = await response.json()
        response.close()

        clientId: str = None
        if jsonResponse is not None and utils.isValidStr(jsonResponse.get('client_id')):
            clientId = utils.getStrFromDict(jsonResponse, 'client_id')

        expiresInSeconds: int = -1
        if jsonResponse is not None and utils.isValidNum(jsonResponse.get('expires_in')):
            expiresInSeconds = utils.getIntFromDict(jsonResponse, 'expires_in')

        if responseStatus != 200 or not utils.isValidStr(clientId) or expiresInSeconds < self.__tokensExpirationBuffer.total_seconds():
            await self.__refreshTokens(
                twitchClientId = twitchClientId,
                twitchClientSecret = twitchClientSecret,
                twitchHandle = twitchHandle
            )
        else:
            await self.__saveUserTokenExpirationTime(
                twitchHandle = twitchHandle,
                expiresInSeconds = expiresInSeconds
            )

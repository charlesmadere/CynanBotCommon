import json
import locale
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional, Set

import aiofiles
import aiofiles.ospath

try:
    import CynanBotCommon.utils as utils
    from CynanBotCommon.network.exceptions import GenericNetworkException
    from CynanBotCommon.timber.timber import Timber
    from CynanBotCommon.twitch.twitchApiService import TwitchApiService
except:
    import utils
    from network.exceptions import GenericNetworkException
    from timber.timber import Timber

    from twitch.twitchApiService import TwitchApiService


class TwitchTokensRepository():

    def __init__(
        self,
        timber: Timber,
        twitchApiService: TwitchApiService,
        twitchTokensFile: str = 'CynanBotCommon/twitch/twitchTokensRepository.json',
        tokensExpirationBuffer: timedelta = timedelta(minutes = 30),
        timeZone: timezone = timezone.utc
    ):
        if not isinstance(timber, Timber):
            raise ValueError(f'timber argument is malformed: \"{timber}\"')
        elif not isinstance(twitchApiService, TwitchApiService):
            raise ValueError(f'twitchApiService argument is malformed: \"{twitchApiService}\"')
        elif not utils.isValidStr(twitchTokensFile):
            raise ValueError(f'twitchTokensFile argument is malformed: \"{twitchTokensFile}\"')
        elif not isinstance(tokensExpirationBuffer, timedelta):
            raise ValueError(f'tokensExpirationBuffer argument is malformed: \"{tokensExpirationBuffer}\"')
        elif not isinstance(timeZone, timezone):
            raise ValueError(f'timeZone argument is malformed: \"{timeZone}\"')

        self.__timber: Timber = timber
        self.__twitchApiService: TwitchApiService = twitchApiService
        self.__twitchTokensFile: str = twitchTokensFile
        self.__tokensExpirationBuffer: timedelta = tokensExpirationBuffer
        self.__timeZone: timezone = timeZone

        self.__jsonCache: Optional[Dict[str, Any]] = None
        self.__tokenExpirations: Dict[str, datetime] = dict()

    async def clearCaches(self):
        self.__jsonCache = None

    async def getAccessToken(self, twitchHandle: str) -> Optional[str]:
        if not utils.isValidStr(twitchHandle):
            raise ValueError(f'twitchHandle argument is malformed: \"{twitchHandle}\"')

        jsonContents = await self.__readJsonForTwitchHandle(twitchHandle)
        return utils.getStrFromDict(jsonContents, 'accessToken', fallback = '')

    async def getExpiringTwitchHandles(self) -> Optional[List[str]]:
        if not utils.hasItems(self.__tokenExpirations):
            return None

        expiringTwitchHandles: Set[str] = set()
        nowDateTime = datetime.now(self.__timeZone)

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

    async def hasAccessToken(self, twitchHandle: str) -> bool:
        if not utils.isValidStr(twitchHandle):
            raise ValueError(f'twitchHandle argument is malformed: \"{twitchHandle}\"')

        accessToken = await self.getAccessToken(twitchHandle)
        return utils.isValidStr(accessToken)

    async def __isDebugLoggingEnabled(self) -> bool:
        jsonContents = await self.__readAllJson()
        return utils.getBoolFromDict(jsonContents, 'debugLoggingEnabled', fallback = True)

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

    async def __refreshTokens(self, twitchHandle: str):
        if not utils.isValidStr(twitchHandle):
            raise ValueError(f'twitchHandle argument is malformed: \"{twitchHandle}\"')

        twitchHandle = twitchHandle.lower()
        self.__timber.log('TwitchTokensRepository', f'Refreshing Twitch tokens for \"{twitchHandle}\"...')

        twitchRefreshToken = await self.requireRefreshToken(twitchHandle)

        try:
            tokens = await self.__twitchApiService.refreshTokens(
                twitchRefreshToken = twitchRefreshToken
            )
        except GenericNetworkException as e:
            self.__timber.log('TwitchTokensRepository', f'Encountered network error when trying to refresh Twitch tokens for \"{twitchHandle}\": {e}', e)
            raise GenericNetworkException(f'TwitchTokensRepository encountered network error when trying to refresh Twitch tokens for \"{twitchHandle}\": {e}')

        jsonContents = await self.__readAllJson()

        jsonContents['twitchHandles'][twitchHandle] = {
            'accessToken': tokens.getAccessToken(),
            'refreshToken': tokens.getRefreshToken()
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
            expiresInSeconds = tokens.getExpiresInSeconds()
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
        elif not utils.isValidInt(expiresInSeconds):
            raise ValueError(f'expiresInSeconds argument is malformed: \"{expiresInSeconds}\"')
        elif expiresInSeconds <= 0:
            raise ValueError(f'expiresInSeconds argument is out of bounds: {expiresInSeconds}')

        twitchHandle = twitchHandle.lower()
        nowDateTime = datetime.now(self.__timeZone)
        expiresInTimeDelta = timedelta(seconds = expiresInSeconds)
        expirationTime = nowDateTime + expiresInTimeDelta
        self.__tokenExpirations[twitchHandle] = expirationTime

        expiresInSecondsStr = locale.format_string("%d", expiresInSeconds, grouping = True)
        self.__timber.log('TwitchTokensRepository', f'Set Twitch tokens for \"{twitchHandle}\" (expiration is in {expiresInSecondsStr} seconds, at {expirationTime})')

        if await self.__isDebugLoggingEnabled():
            self.__timber.log('TwitchTokensRepository', f'tokenExpirations contents: {self.__tokenExpirations}')

    async def validateAndRefreshAccessToken(self, twitchHandle: str):
        if not utils.isValidStr(twitchHandle):
            raise ValueError(f'twitchHandle argument is malformed: \"{twitchHandle}\"')

        twitchHandle = twitchHandle.lower()
        self.__timber.log('TwitchTokensRepository', f'Validating Twitch tokens for \"{twitchHandle}\"...')

        twitchAccessToken = await self.requireAccessToken(twitchHandle)

        expiresInSeconds: Optional[int] = None
        try:
            expiresInSeconds = await self.__twitchApiService.validateTokens(
                twitchAccessToken = twitchAccessToken
            )
        except GenericNetworkException as e:
            self.__timber.log('TwitchTokensRepository', f'Encountered network error when trying to validate Twitch tokens for \"{twitchHandle}\": {e}', e)
            raise GenericNetworkException(f'TwitchTokensRepository encountered network error when trying to validate Twitch tokens for \"{twitchHandle}\": {e}')

        if utils.isValidInt(expiresInSeconds) and expiresInSeconds >= self.__tokensExpirationBuffer.total_seconds():
            await self.__saveUserTokenExpirationTime(
                twitchHandle = twitchHandle,
                expiresInSeconds = expiresInSeconds
            )
        else:
            await self.__refreshTokens(twitchHandle)

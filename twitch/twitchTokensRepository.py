import json
import locale
import traceback
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional, Set

import aiofiles
import aiofiles.ospath

try:
    import CynanBotCommon.utils as utils
    from CynanBotCommon.network.exceptions import GenericNetworkException
    from CynanBotCommon.storage.backingDatabase import BackingDatabase
    from CynanBotCommon.storage.databaseConnection import DatabaseConnection
    from CynanBotCommon.storage.databaseType import DatabaseType
    from CynanBotCommon.timber.timber import Timber
    from CynanBotCommon.twitch.twitchApiService import TwitchApiService
    from CynanBotCommon.twitch.twitchTokensRepositoryInterface import \
        TwitchTokensRepositoryInterface
except:
    import utils
    from network.exceptions import GenericNetworkException
    from storage.backingDatabase import BackingDatabase
    from storage.databaseConnection import DatabaseConnection
    from storage.databaseType import DatabaseType
    from timber.timber import Timber

    from twitch.twitchApiService import TwitchApiService
    from twitch.twitchTokensRepositoryInterface import \
        TwitchTokensRepositoryInterface


class TwitchTokensRepository(TwitchTokensRepositoryInterface):

    def __init__(
        self,
        backingDatabase: BackingDatabase,
        timber: Timber,
        twitchApiService: TwitchApiService,
        seedFile: Optional[str] = None,
        twitchTokensFile: str = 'CynanBotCommon/twitch/twitchTokensRepository.json',
        tokensExpirationBuffer: timedelta = timedelta(minutes = 15),
        timeZone: timezone = timezone.utc
    ):
        if not isinstance(backingDatabase, BackingDatabase):
            raise ValueError(f'backingDatabase argument is malformed: \"{backingDatabase}\"')
        elif not isinstance(timber, Timber):
            raise ValueError(f'timber argument is malformed: \"{timber}\"')
        elif not isinstance(twitchApiService, TwitchApiService):
            raise ValueError(f'twitchApiService argument is malformed: \"{twitchApiService}\"')
        elif seedFile is not None and not isinstance(seedFile, str):
            raise ValueError(f'seedFile argument is malformed: \"{seedFile}\"')
        elif not utils.isValidStr(twitchTokensFile):
            raise ValueError(f'twitchTokensFile argument is malformed: \"{twitchTokensFile}\"')
        elif not isinstance(tokensExpirationBuffer, timedelta):
            raise ValueError(f'tokensExpirationBuffer argument is malformed: \"{tokensExpirationBuffer}\"')
        elif not isinstance(timeZone, timezone):
            raise ValueError(f'timeZone argument is malformed: \"{timeZone}\"')

        self.__backingDatabase: BackingDatabase = backingDatabase
        self.__timber: Timber = timber
        self.__twitchApiService: TwitchApiService = twitchApiService
        self.__seedFile: Optional[str] = seedFile
        self.__twitchTokensFile: str = twitchTokensFile
        self.__tokensExpirationBuffer: timedelta = tokensExpirationBuffer
        self.__timeZone: timezone = timeZone

        self.__jsonCache: Optional[Dict[str, Any]] = None
        self.__tokenExpirations: Dict[str, datetime] = dict()

    async def addUser(self, twitchHandle: str, code: str):
        if not utils.isValidStr(twitchHandle):
            raise ValueError(f'twitchHandle argument is malformed: \"{twitchHandle}\"')
        elif not utils.isValidStr(code):
            raise ValueError(f'code argument is malformed: \"{code}\"')

        twitchHandle = twitchHandle.lower()
        self.__timber.log('TwitchTokensRepository', f'Adding user \"{twitchHandle}\"...')

        if await self.hasAccessToken(twitchHandle):
            self.__timber.log('TwitchTokensRepository', f'User \"{twitchHandle}\" already has Twitch tokens that are going to be overwritten!')

        try:
            tokens = await self.__twitchApiService.fetchTokens(code = code)
        except GenericNetworkException as e:
            self.__timber.log('TwitchTokensRepository', f'Encountered network error when trying to add user \"{twitchHandle}\": {e}', e, traceback.format_exc())
            raise GenericNetworkException(f'TwitchTokensRepository encountered network error when trying to add user \"{twitchHandle}\": {e}')

        jsonContents = await self.__readAllJson()

        jsonContents['twitchHandles'][twitchHandle] = {
            'accessToken': tokens.getAccessToken(),
            'refreshToken': tokens.getRefreshToken()
        }

        await self.__flush(jsonContents)

    async def clearCaches(self):
        self.__jsonCache = None

    async def __flush(self, jsonContents: Dict[str, Any]):
        if not utils.hasItems(jsonContents):
            raise ValueError(f'jsonContents argument is malformed: \"{jsonContents}\"')

        jsonString: str = ''
        async with aiofiles.open(self.__twitchTokensFile, mode = 'w') as file:
            jsonString = json.dumps(jsonContents, indent = 4, sort_keys = True)
            await file.write(jsonString)

        # be sure to clear caches, as JSON file contents have now been updated
        await self.clearCaches()

        if await self.__isDebugLoggingEnabled():
            self.__timber.log('TwitchTokensRepository', f'{self.__twitchTokensFile} contents: {jsonString}')

    async def getAccessToken(self, twitchHandle: str) -> Optional[str]:
        if not utils.isValidStr(twitchHandle):
            raise ValueError(f'twitchHandle argument is malformed: \"{twitchHandle}\"')

        jsonContents = await self.__readJsonForTwitchHandle(twitchHandle)
        accessToken = utils.getStrFromDict(jsonContents, 'accessToken', fallback = '')

        if utils.isValidStr(accessToken):
            return accessToken
        else:
            return None    

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

            for key in twitchHandlesJson.keys():
                if key.lower() not in self.__tokenExpirations:
                    expiringTwitchHandles.add(key.lower())
                    self.__timber.log('TwitchTokensRepository', f'Discovered new PubSub user: \"{key}\"!')

        return list(expiringTwitchHandles)

    async def getRefreshToken(self, twitchHandle: str) -> Optional[str]:
        if not utils.isValidStr(twitchHandle):
            raise ValueError(f'twitchHandle argument is malformed: \"{twitchHandle}\"')

        jsonContents = await self.__readJsonForTwitchHandle(twitchHandle)
        refreshToken = utils.getStrFromDict(jsonContents, 'refreshToken', fallback = '')

        if utils.isValidStr(refreshToken):
            return refreshToken
        else:
            return None

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
        twitchHandlesJson: Optional[Dict[str, Any]] = jsonContents.get('twitchHandles')

        if twitchHandlesJson is None:
            return dict()
        else:
            return twitchHandlesJson

    async def __readJsonForTwitchHandle(self, twitchHandle: str) -> Dict[str, Any]:
        if not utils.isValidStr(twitchHandle):
            raise ValueError(f'twitchHandle argument is malformed: \"{twitchHandle}\"')

        twitchHandlesJson = await self.__readAllTwitchHandleJson()
        twitchHandle = twitchHandle.lower()

        for key, userJson in twitchHandlesJson.items():
            if key.lower() == twitchHandle:
                return userJson

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
            self.__timber.log('TwitchTokensRepository', f'Encountered network error when trying to refresh Twitch tokens for \"{twitchHandle}\": {e}', e, traceback.format_exc())
            raise GenericNetworkException(f'TwitchTokensRepository encountered network error when trying to refresh Twitch tokens for \"{twitchHandle}\": {e}')

        jsonContents = await self.__readAllJson()

        jsonContents['twitchHandles'][twitchHandle] = {
            'accessToken': tokens.getAccessToken(),
            'refreshToken': tokens.getRefreshToken()
        }

        await self.__flush(jsonContents)

        await self.__saveUserTokenExpirationTime(
            twitchHandle = twitchHandle,
            expiresInSeconds = tokens.getExpiresInSeconds()
        )

    async def removeUser(self, twitchHandle: str):
        if not utils.isValidStr(twitchHandle):
            raise ValueError(f'twitchHandle argument is malformed: \"{twitchHandle}\"')

        twitchHandle = twitchHandle.lower()
        self.__timber.log('TwitchTokensRepository', f'Adding user \"{twitchHandle}\"...')

        if not await self.hasAccessToken(twitchHandle):
            self.__timber.log(f'Attempted to remove user \"{twitchHandle}\", but they do not have Twitch tokens')
            return

        jsonContents = await self.__readAllJson()

        if twitchHandle in jsonContents['twitchHandles']:
            del jsonContents['twitchHandles'][twitchHandle]

        await self.__flush(jsonContents)

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
            self.__timber.log('TwitchTokensRepository', f'Encountered network error when trying to validate Twitch tokens for \"{twitchHandle}\": {e}', e, traceback.format_exc())
            raise GenericNetworkException(f'TwitchTokensRepository encountered network error when trying to validate Twitch tokens for \"{twitchHandle}\": {e}')

        if utils.isValidInt(expiresInSeconds) and expiresInSeconds >= self.__tokensExpirationBuffer.total_seconds():
            await self.__saveUserTokenExpirationTime(
                twitchHandle = twitchHandle,
                expiresInSeconds = expiresInSeconds
            )
        else:
            await self.__refreshTokens(twitchHandle)

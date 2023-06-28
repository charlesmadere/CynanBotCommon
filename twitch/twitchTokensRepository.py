import json
import os
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
    from CynanBotCommon.twitch.exceptions import (
        NoTwitchTokenDetailsException, TwitchPasswordChangedException)
    from CynanBotCommon.twitch.twitchApiService import TwitchApiService
    from CynanBotCommon.twitch.twitchTokensDetails import TwitchTokensDetails
    from CynanBotCommon.twitch.twitchTokensRepositoryInterface import \
        TwitchTokensRepositoryInterface
except:
    import utils
    from network.exceptions import GenericNetworkException
    from storage.backingDatabase import BackingDatabase
    from storage.databaseConnection import DatabaseConnection
    from storage.databaseType import DatabaseType
    from timber.timber import Timber

    from twitch.exceptions import (NoTwitchTokenDetailsException,
                                   TwitchPasswordChangedException)
    from twitch.twitchApiService import TwitchApiService
    from twitch.twitchTokensDetails import TwitchTokensDetails
    from twitch.twitchTokensRepositoryInterface import \
        TwitchTokensRepositoryInterface


class TwitchTokensRepository(TwitchTokensRepositoryInterface):

    def __init__(
        self,
        backingDatabase: BackingDatabase,
        timber: Timber,
        twitchApiService: TwitchApiService,
        seedFile: Optional[str] = 'CynanBotCommon/twitch/twitchTokensRepositorySeedFile.json',
        tokensExpirationBuffer: timedelta = timedelta(minutes = 10),
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
        elif not isinstance(tokensExpirationBuffer, timedelta):
            raise ValueError(f'tokensExpirationBuffer argument is malformed: \"{tokensExpirationBuffer}\"')
        elif not isinstance(timeZone, timezone):
            raise ValueError(f'timeZone argument is malformed: \"{timeZone}\"')

        self.__backingDatabase: BackingDatabase = backingDatabase
        self.__timber: Timber = timber
        self.__twitchApiService: TwitchApiService = twitchApiService
        self.__seedFile: Optional[str] = seedFile
        self.__tokensExpirationBuffer: timedelta = tokensExpirationBuffer
        self.__timeZone: timezone = timeZone

        self.__isDatabaseReady: bool = False
        self.__cache: Dict[str, TwitchTokensDetails] = dict()
        self.__tokenExpirationTimes: Dict[str, datetime] = dict()

    async def addUser(self, code: str, twitchChannel: str):
        if not utils.isValidStr(code):
            raise ValueError(f'code argument is malformed: \"{code}\"')
        elif not utils.isValidStr(twitchChannel):
            raise ValueError(f'twitchChannel argument is malformed: \"{twitchChannel}\"')

        self.__timber.log('TwitchTokensRepository', f'Adding user \"{twitchChannel}\"...')

        try:
            tokensDetails = await self.__twitchApiService.fetchTokens(code = code)
        except GenericNetworkException as e:
            self.__timber.log('TwitchTokensRepository', f'Encountered network error when trying to add user \"{twitchChannel}\": {e}', e, traceback.format_exc())
            raise GenericNetworkException(f'TwitchTokensRepository encountered network error when trying to add user \"{twitchChannel}\": {e}')

        await self.__setTokensDetails(
            tokensDetails = tokensDetails,
            twitchChannel = twitchChannel
        )

    async def clearCaches(self):
        self.__cache.clear()

    async def __consumeSeedFile(self):
        seedFile = self.__seedFile

        if not utils.isValidStr(seedFile):
            return

        self.__seedFile = None

        if not await aiofiles.ospath.exists(seedFile):
            self.__timber.log('TwitchTokensRepository', f'Seed file (\"{seedFile}\") does not exist')
            return

        async with aiofiles.open(seedFile, mode = 'r') as file:
            data = await file.read()
            jsonContents: Optional[Dict[str, Dict[str, Any]]] = json.loads(data)

        # I don't believe there is an aiofiles version of this call at this time (June 23rd, 2023).
        os.remove(seedFile)

        if not utils.hasItems(jsonContents):
            self.__timber.log('TwitchTokensRepository', f'Seed file (\"{seedFile}\") is empty')
            return

        self.__timber.log('TwitchTokensRepository', f'Reading in seed file \"{seedFile}\"...')

        for twitchChannel, tokensDetailsJson in jsonContents.items():
            tokensDetails = TwitchTokensDetails(
                expirationTime = await self.__createExpiredExpirationTime(),
                accessToken = utils.getStrFromDict(tokensDetailsJson, 'accessToken'),
                refreshToken = utils.getStrFromDict(tokensDetailsJson, 'refreshToken')
            )

            await self.__setTokensDetails(
                tokensDetails = tokensDetails,
                twitchChannel = twitchChannel
            )

        self.__timber.log('TwitchTokensRepository', f'Finished reading in seed file \"{seedFile}\"')

    async def __createExpiredExpirationTime(self) -> datetime:
        nowDateTime = datetime.now(self.__timeZone)
        return nowDateTime - timedelta(weeks = 1)

    async def getAccessToken(self, twitchChannel: str) -> Optional[str]:
        if not utils.isValidStr(twitchChannel):
            raise ValueError(f'twitchChannel argument is malformed: \"{twitchChannel}\"')

        tokensDetails = await self.getTokensDetails(twitchChannel)

        if tokensDetails is None:
            return None

        return tokensDetails.getAccessToken()

    async def __getDatabaseConnection(self) -> DatabaseConnection:
        await self.__initDatabaseTable()
        return await self.__backingDatabase.getConnection()

    async def getExpiringTwitchChannels(self) -> Optional[List[str]]:
        if not utils.hasItems(self.__tokenExpirationTimes):
            return None

        expiringTwitchChannels: Set[str] = set()
        nowDateTime = datetime.now(self.__timeZone)

        for twitchChannel, expirationDateTime in self.__tokenExpirationTimes.items():
            if expirationDateTime is None or nowDateTime + self.__tokensExpirationBuffer >= expirationDateTime:
                expiringTwitchChannels.add(twitchChannel.lower())

        return list(expiringTwitchChannels)

    async def getRefreshToken(self, twitchChannel: str) -> Optional[str]:
        if not utils.isValidStr(twitchChannel):
            raise ValueError(f'twitchChannel argument is malformed: \"{twitchChannel}\"')

        tokensDetails = await self.getTokensDetails(twitchChannel)

        if tokensDetails is None:
            return None

        return tokensDetails.getRefreshToken()

    async def getTokensDetails(self, twitchChannel: str) -> Optional[TwitchTokensDetails]:
        if not utils.isValidStr(twitchChannel):
            raise ValueError(f'twitchChannel argument is malformed: \"{twitchChannel}\"')

        if twitchChannel.lower() in self.__cache:
            return self.__cache[twitchChannel.lower()]

        connection = await self.__getDatabaseConnection()
        record = await connection.fetchRow(
            '''
                SELECT expirationtime, accesstoken, refreshtoken FROM twitchtokens
                WHERE twitchchannel = $1
                LIMIT 1
            ''',
            twitchChannel
        )

        await connection.close()

        if not utils.hasItems(record):
            self.__cache.pop(twitchChannel.lower(), None)
            return None

        expirationTime = utils.getDateTimeFromStr(record[0])
        expiresInSeconds = 0

        if utils.isValidStr(expirationTime):
            nowDateTime = datetime.now(self.__timeZone)
            expiresInTimeDelta: timedelta = expirationTime - nowDateTime
            expiresInSeconds = expiresInTimeDelta.total_seconds()

        tokensDetails = TwitchTokensDetails(
            expirationTime = expiresInSeconds,
            accessToken = record[1],
            refreshToken = record[2]
        )

        self.__cache[twitchChannel.lower()] = tokensDetails
        self.__tokenExpirationTimes[twitchChannel.lower()] = tokensDetails.getExpirationTime()

        return tokensDetails

    async def hasAccessToken(self, twitchChannel: str) -> bool:
        if not utils.isValidStr(twitchChannel):
            raise ValueError(f'twitchChannel argument is malformed: \"{twitchChannel}\"')

        accessToken = await self.getAccessToken(twitchChannel)
        return utils.isValidStr(accessToken)

    async def __initDatabaseTable(self):
        if self.__isDatabaseReady:
            return

        self.__isDatabaseReady = True
        connection = await self.__backingDatabase.getConnection()

        if connection.getDatabaseType() is DatabaseType.POSTGRESQL:
            await connection.createTableIfNotExists(
                '''
                    CREATE TABLE IF NOT EXISTS twitchtokens (
                        expirationtime text DEFAULT NULL,
                        accesstoken text NOT NULL,
                        refreshtoken text NOT NULL,
                        twitchchannel public.citext NOT NULL PRIMARY KEY
                    )
                '''
            )
        elif connection.getDatabaseType() is DatabaseType.SQLITE:
            await connection.createTableIfNotExists(
                '''
                    CREATE TABLE IF NOT EXISTS twitchtokens (
                        expirationtime TEXT DEFAULT NULL,
                        accesstoken TEXT NOT NULL,
                        refreshtoken TEXT NOT NULL,
                        twitchchannel TEXT NOT NULL PRIMARY KEY COLLATE NOCASE
                    )
                '''
            )
        else:
            raise RuntimeError(f'Encountered unexpected DatabaseType when trying to create tables: \"{connection.getDatabaseType()}\"')

        await connection.close()
        await self.__consumeSeedFile()

    async def __refreshTokensDetails(
        self,
        twitchChannel: str,
        tokensDetails: TwitchTokensDetails
    ):
        if not isinstance(tokensDetails, TwitchTokensDetails):
            raise ValueError(f'tokenDetails argument is malformed: \"{tokensDetails}\"')
        elif not utils.isValidStr(twitchChannel):
            raise ValueError(f'twitchChannel argument is malformed: \"{twitchChannel}\"')

        self.__timber.log('TwitchTokensRepository', f'Refreshing Twitch tokens for \"{twitchChannel}\"...')

        try:
            newTokensDetails = await self.__twitchApiService.refreshTokens(
                twitchRefreshToken = tokensDetails.getRefreshToken()
            )
        except GenericNetworkException as e:
            self.__timber.log('TwitchTokensRepository', f'Encountered network error when trying to refresh Twitch tokens for \"{twitchChannel}\": {e}', e, traceback.format_exc())
            raise GenericNetworkException(f'TwitchTokensRepository encountered network error when trying to refresh Twitch tokens for \"{twitchChannel}\": {e}')
        except TwitchPasswordChangedException as e:
            self.__timber.log('TwitchTokensRepository', f'Encountered network error caused by password change when trying to refresh Twitch tokens for \"{twitchChannel}\": {e}', e, traceback.format_exc())
            await self.removeUser(twitchChannel)
            raise TwitchPasswordChangedException(f'TwitchTokensRepository encountered network error caused by password change when trying to refresh Twitch tokens for \"{twitchChannel}\": {e}')

        await self.__setTokensDetails(
            tokensDetails = newTokensDetails,
            twitchChannel = twitchChannel
        )

    async def removeUser(self, twitchChannel: str):
        if not utils.isValidStr(twitchChannel):
            raise ValueError(f'twitchChannel argument is malformed: \"{twitchChannel}\"')

        self.__timber.log('TwitchTokensRepository', f'Removing user \"{twitchChannel}\"...')

        connection = await self.__getDatabaseConnection()
        await connection.execute(
            '''
                DELETE FROM twitchtokens
                WHERE twitchchannel = $1
            ''',
            twitchChannel
        )

        await connection.close()
        self.__cache.pop(twitchChannel.lower(), None)
        self.__tokenExpirationTimes.pop(twitchChannel.lower(), None)

    async def requireAccessToken(self, twitchChannel: str) -> str:
        if not utils.isValidStr(twitchChannel):
            raise ValueError(f'twitchChannel argument is malformed: \"{twitchChannel}\"')

        accessToken = await self.getAccessToken(twitchChannel)

        if not utils.isValidStr(accessToken):
            raise ValueError(f'\"accessToken\" value for \"{twitchChannel}\" in \"{self.__twitchTokensFile}\" is malformed: \"{accessToken}\"')

        return accessToken

    async def requireRefreshToken(self, twitchChannel: str) -> str:
        if not utils.isValidStr(twitchChannel):
            raise ValueError(f'twitchChannel argument is malformed: \"{twitchChannel}\"')

        refreshToken = await self.getRefreshToken(twitchChannel)

        if not utils.isValidStr(refreshToken):
            raise ValueError(f'\"refreshToken\" value for \"{twitchChannel}\" in \"{self.__twitchTokensFile}\" is malformed: \"{refreshToken}\"')

        return refreshToken

    async def requireTokensDetails(self, twitchChannel: str) -> TwitchTokensDetails:
        if not utils.isValidStr(twitchChannel):
            raise ValueError(f'twitchChannel argument is malformed: \"{twitchChannel}\"')

        tokensDetails = await self.getTokensDetails(twitchChannel)

        if tokensDetails is None:
            raise NoTwitchTokenDetailsException(f'Twitch tokens details for \"{twitchChannel}\" is missing/unavailable')

        return tokensDetails

    async def __setExpirationTime(
        self,
        expirationTime: datetime,
        twitchChannel: str
    ):
        if not isinstance(expirationTime, datetime):
            raise ValueError(f'expirationTime argument is malformed: \"{expirationTime}\"')
        elif not utils.isValidStr(twitchChannel):
            raise ValueError(f'twitchChannel argument is malformed: \"{twitchChannel}\"')

        connection = await self.__getDatabaseConnection()
        await connection.execute(
            '''
                UPDATE twitchtokens
                SET expirationtime = $1
                WHERE twitchchannel = $2
            ''',
            expirationTime.isoformat(), twitchChannel
        )

        await connection.close()
        self.__cache.pop(twitchChannel.lower(), None)
        self.__tokenExpirationTimes[twitchChannel.lower()] = expirationTime

    async def __setTokensDetails(
        self,
        tokensDetails: Optional[TwitchTokensDetails],
        twitchChannel: str
    ):
        if tokensDetails is not None and not isinstance(tokensDetails, TwitchTokensDetails):
            raise ValueError(f'tokenDetails argument is malformed: \"{tokensDetails}\"')
        elif not utils.isValidStr(twitchChannel):
            raise ValueError(f'twitchChannel argument is malformed: \"{twitchChannel}\"')

        connection = await self.__getDatabaseConnection()

        if tokensDetails is None:
            await connection.execute(
                '''
                    DELETE FROM twitchtokens
                    WHERE twitchchannel = $1
                ''',
                twitchChannel
            )

            self.__cache.pop(twitchChannel.lower(), None)
            self.__tokenExpirationTimes.pop(twitchChannel.lower(), None)
            self.__timber.log('TwitchTokensRepository', f'Twitch tokens details for \"{twitchChannel}\" has been deleted')
        else:
            expirationTime = tokensDetails.getExpirationTime()

            await connection.execute(
                '''
                    INSERT INTO twitchtokens (expirationtime, accesstoken, refreshtoken, twitchchannel)
                    VALUES ($1, $2, $3, $4)
                    ON CONFLICT (twitchchannel) DO UPDATE SET expirationtime = EXCLUDED.expirationtime, accesstoken = EXCLUDED.accesstoken, refreshtoken = EXCLUDED.refreshtoken
                ''',
                expirationTime.isoformat(), tokensDetails.getAccessToken(), tokensDetails.getRefreshToken(), twitchChannel
            )

            self.__cache[twitchChannel.lower()] = tokensDetails
            self.__tokenExpirationTimes[twitchChannel.lower()] = expirationTime
            self.__timber.log('TwitchTokensRepository', f'Twitch tokens details for \"{twitchChannel}\" has been updated ({tokensDetails})')

        await connection.close()

    async def validateAndRefreshAccessToken(self, twitchChannel: str):
        if not utils.isValidStr(twitchChannel):
            raise ValueError(f'twitchChannel argument is malformed: \"{twitchChannel}\"')

        tokensDetails = await self.getTokensDetails(twitchChannel)

        if tokensDetails is None:
            self.__timber.log('TwitchTokensRepository', f'Attempted to validate Twitch tokens for \"{twitchChannel}\", but tokens details are missing/unavailable')
            return

        self.__timber.log('TwitchTokensRepository', f'Validating Twitch tokens for \"{twitchChannel}\"...')

        expirationTime: Optional[datetime] = None
        try:
            expirationTime = await self.__twitchApiService.validateTokens(
                twitchAccessToken = tokensDetails.getAccessToken()
            )
        except GenericNetworkException as e:
            self.__timber.log('TwitchTokensRepository', f'Encountered network error when trying to validate Twitch tokens for \"{twitchChannel}\": {e}', e, traceback.format_exc())
            raise GenericNetworkException(f'TwitchTokensRepository encountered network error when trying to validate Twitch tokens for \"{twitchChannel}\": {e}')

        nowDateTime = datetime.now(self.__timeZone)

        if expirationTime is not None and expirationTime > nowDateTime + self.__tokensExpirationBuffer:
            await self.__setExpirationTime(
                expirationTime = expirationTime,
                twitchChannel = twitchChannel
            )
        else:
            await self.__refreshTokensDetails(
                twitchChannel = twitchChannel,
                tokensDetails = tokensDetails
            )

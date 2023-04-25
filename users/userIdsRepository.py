from typing import Optional

try:
    import CynanBotCommon.utils as utils
    from CynanBotCommon.network.exceptions import GenericNetworkException
    from CynanBotCommon.storage.backingDatabase import BackingDatabase
    from CynanBotCommon.storage.databaseConnection import DatabaseConnection
    from CynanBotCommon.storage.databaseType import DatabaseType
    from CynanBotCommon.timber.timber import Timber
    from CynanBotCommon.twitch.twitchApiService import TwitchApiService
    from CynanBotCommon.twitch.twitchUserDetails import TwitchUserDetails
except:
    import utils
    from network.exceptions import GenericNetworkException
    from storage.backingDatabase import BackingDatabase
    from storage.databaseConnection import DatabaseConnection
    from storage.databaseType import DatabaseType
    from timber.timber import Timber
    from twitch.twitchApiService import TwitchApiService
    from twitch.twitchUserDetails import TwitchUserDetails


class UserIdsRepository():

    def __init__(
        self,
        backingDatabase: BackingDatabase,
        timber: Timber,
        twitchApiService: TwitchApiService
    ):
        if not isinstance(backingDatabase, BackingDatabase):
            raise ValueError(f'backingDatabase argument is malformed: \"{backingDatabase}\"')
        elif not isinstance(timber, Timber):
            raise ValueError(f'timber argument is malformed: \"{timber}\"')
        elif not isinstance(twitchApiService, TwitchApiService):
            raise ValueError(f'twitchApiService argument is malformed: \"{twitchApiService}\"')

        self.__backingDatabase: BackingDatabase = backingDatabase
        self.__timber: Timber = timber
        self.__twitchApiService: TwitchApiService = twitchApiService

        self.__isDatabaseReady: bool = False

    async def fetchUserId(
        self,
        userName: str,
        twitchAccessToken: Optional[str] = None
    ) -> str:
        if not utils.isValidStr(userName):
            raise ValueError(f'userName argument is malformed: \"{userName}\"')

        connection = await self.__getDatabaseConnection()
        record = await connection.fetchRow(
            '''
                SELECT userid FROM userids
                WHERE username = $1
                LIMIT 1
            ''',
            userName
        )

        userId: Optional[str] = None
        if utils.hasItems(record):
            userId = record[0]

        await connection.close()

        if utils.isValidStr(userId):
            return userId
        elif not utils.isValidStr(twitchAccessToken):
            raise RuntimeError(f'UserIdsRepository can\'t lookup Twitch user ID for \"{userName}\" as no twitchAccessToken was specified')

        self.__timber.log('UserIdsRepository', f'User ID for userName \"{userName}\" wasn\'t found locally, so performing a network call to fetch instead...')

        userDetails: Optional[TwitchUserDetails] = None

        try:
            userDetails = await self.__twitchApiService.fetchUserDetails(
                twitchAccessToken = twitchAccessToken,
                userName = userName
            )
        except GenericNetworkException as e:
            self.__timber.log('UserIdsRepository', f'Received a network error of some kind when fetching userId for userName \"{userName}\": {e}', e)
            raise GenericNetworkException(f'UserIdsRepository received a network error of some kind when fetching userId for userName \"{userName}\": {e}')

        if userDetails is None:
            raise RuntimeError(f'Unable to retrieve user ID for userName \"{userName}\" from the Twitch API')

        userId = userDetails.getUserId()
        await self.setUser(userId = userId, userName = userName)

        return userId

    async def fetchUserIdAsInt(
        self,
        userName: str,
        twitchAccessToken: Optional[str] = None
    ) -> int:
        userId = await self.fetchUserId(
            userName = userName,
            twitchAccessToken = twitchAccessToken
        )

        return int(userId)

    async def fetchUserName(self, userId: str) -> str:
        if not utils.isValidStr(userId):
            raise ValueError(f'userId argument is malformed: \"{userId}\"')
        elif userId == '0':
            raise ValueError(f'userId argument is an illegal value: \"{userId}\"')

        connection = await self.__getDatabaseConnection()
        record = await connection.fetchRow(
            '''
                SELECT username FROM userids
                WHERE userid = $1
                LIMIT 1
            ''',
            userId
        )

        if not utils.hasItems(record):
            raise RuntimeError(f'No userName for userId \"{userId}\" found')

        userName: Optional[str] = record[0]
        if not utils.isValidStr(userName):
            raise RuntimeError(f'userName for userId \"{userId}\" is malformed: \"{userName}\"')

        await connection.close()
        return userName

    async def __getDatabaseConnection(self) -> DatabaseConnection:
        await self.__initDatabaseTable()
        return await self.__backingDatabase.getConnection()

    async def __initDatabaseTable(self):
        if self.__isDatabaseReady:
            return

        self.__isDatabaseReady = True
        connection = await self.__backingDatabase.getConnection()

        if connection.getDatabaseType() is DatabaseType.POSTGRESQL:
            await connection.createTableIfNotExists(
                '''
                    CREATE TABLE IF NOT EXISTS userids (
                        userid public.citext NOT NULL PRIMARY KEY,
                        username public.citext NOT NULL
                    )
                '''
            )
        elif connection.getDatabaseType() is DatabaseType.SQLITE:
            await connection.createTableIfNotExists(
                '''
                    CREATE TABLE IF NOT EXISTS userids (
                        userid TEXT NOT NULL PRIMARY KEY COLLATE NOCASE,
                        username TEXT NOT NULL COLLATE NOCASE
                    )
                '''
            )
        else:
            raise RuntimeError(f'Encountered unexpected DatabaseType when trying to create tables: \"{connection.getDatabaseType()}\"')

        await connection.close()

    async def setUser(self, userId: str, userName: str):
        if not utils.isValidStr(userId):
            raise ValueError(f'userId argument is malformed: \"{userId}\"')
        elif userId == '0':
            raise ValueError(f'userId argument is an illegal value: \"{userId}\"')
        elif not utils.isValidStr(userName):
            raise ValueError(f'userName argument is malformed: \"{userName}\"')

        connection = await self.__getDatabaseConnection()
        await connection.execute(
            '''
                INSERT INTO userids (userid, username)
                VALUES ($1, $2)
                ON CONFLICT (userid) DO UPDATE SET username = EXCLUDED.username
            ''',
            userId, userName
        )

        await connection.close()

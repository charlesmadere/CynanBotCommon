from typing import Any, Dict, Optional

try:
    import CynanBotCommon.utils as utils
    from CynanBotCommon.network.exceptions import GenericNetworkException
    from CynanBotCommon.network.networkClientProvider import \
        NetworkClientProvider
    from CynanBotCommon.storage.backingDatabase import BackingDatabase
    from CynanBotCommon.storage.databaseConnection import DatabaseConnection
    from CynanBotCommon.timber.timber import Timber
except:
    import utils
    from network.exceptions import GenericNetworkException
    from network.networkClientProvider import NetworkClientProvider
    from storage.backingDatabase import BackingDatabase
    from storage.databaseConnection import DatabaseConnection
    from timber.timber import Timber


class UserIdsRepository():

    def __init__(
        self,
        backingDatabase: BackingDatabase,
        networkClientProvider: NetworkClientProvider,
        timber: Timber
    ):
        if backingDatabase is None:
            raise ValueError(f'backingDatabase argument is malformed: \"{backingDatabase}\"')
        elif networkClientProvider is None:
            raise ValueError(f'networkClientProvider argument is malformed: \"{networkClientProvider}\"')
        elif timber is None:
            raise ValueError(f'timber argument is malformed: \"{timber}\"')

        self.__backingDatabase: BackingDatabase = backingDatabase
        self.__networkClientProvider: NetworkClientProvider = networkClientProvider
        self.__timber: Timber = timber

        self.__isDatabaseReady: bool = False

    async def fetchUserId(
        self,
        userName: str,
        twitchAccessToken: Optional[str] = None,
        twitchClientId: Optional[str] = None
    ) -> str:
        if not utils.isValidStr(userName):
            raise ValueError(f'userName argument is malformed: \"{userName}\"')

        connection = await self.__getDatabaseConnection()
        record = await connection.fetchRow(
            '''
                SELECT userId FROM userIds
                WHERE userName = $1
            ''',
            userName
        )

        userId: str = None
        if utils.hasItems(record):
            userId = record[0]

        await connection.close()

        if userId is not None:
            if utils.isValidStr(userId):
                return userId
            else:
                self.__timber.log('UserIdsRepository', f'Persisted userId for userName \"{userName}\" is malformed: \"{userId}\"')
                raise RuntimeError(f'Persisted userId for userName \"{userName}\" is malformed: \"{userId}\"')

        if not utils.isValidStr(twitchAccessToken) or not utils.isValidStr(twitchClientId):
            raise ValueError(f'Can\'t lookup Twitch user ID for \"{userName}\", as twitchAccessToken (\"{twitchAccessToken}\") and/or twitchClientId (\"{twitchClientId}\") is malformed')

        self.__timber.log('UserIdsRepository', f'Performing network call to fetch Twitch userId for userName \"{userName}\"...')

        clientSession = await self.__networkClientProvider.get()

        try:
            response = await clientSession.get(
                url = f'https://api.twitch.tv/helix/users?login={userName}',
                headers = {
                    'Authorization': f'Bearer {twitchAccessToken}',
                    'Client-Id': twitchClientId
                }
            )
        except GenericNetworkException as e:
            self.__timber.log('UserIdsRepository', f'Encountered network error when fetching userId for userName \"{userName}\": {e}', e)
            raise RuntimeError(f'UserIdsRepository encountered network error when fetching userId for userName \"{userName}\": {e}')

        if response.getStatusCode() != 200:
            self.__timber.log('UserIdsRepository', f'Encountered non-200 HTTP status code when fetching userId for userName \"{userName}\": \"{response.getStatusCode()}\"')
            raise RuntimeError(f'UserIdsRepository encountered non-200 HTTP status code when fetching userId for userName \"{userName}\": \"{response.getStatusCode()}\"')

        jsonResponse: Optional[Dict[str, Any]] = await response.json()
        await response.close()

        if 'error' in jsonResponse and len(jsonResponse['error']) >= 1:
            self.__timber.log('UserIdsRepository', f'Received an error of some kind when fetching userId for userName \"{userName}\": {jsonResponse}')
            raise RuntimeError(f'UserIdsRepository received an error of some kind when fetching userId for userName \"{userName}\": {jsonResponse}')

        userId: Optional[str] = jsonResponse['data'][0]['id']

        if not utils.isValidStr(userId):
            self.__timber.log('UserIdsRepository', f'Unable to fetch userId for \"{userName}\": {jsonResponse}')
            raise ValueError(f'UserIdsRepository was unable to fetch userId for \"{userName}\": {jsonResponse}')

        self.__timber.log('UserIdsRepository', f'Successfully fetched Twitch userId for userName \"{userName}\": \"{userId}\"')
        await self.setUser(userId = userId, userName = userName)

        return userId

    async def fetchUserIdAsInt(
        self,
        userName: str,
        twitchAccessToken: Optional[str] = None,
        twitchClientId: Optional[str] = None
    ) -> int:
        userId = await self.fetchUserId(
            userName = userName,
            twitchAccessToken = twitchAccessToken,
            twitchClientId = twitchClientId
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
                SELECT userName FROM userIds
                WHERE userId = $1
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
        await connection.execute(
            '''
                CREATE TABLE IF NOT EXISTS userIds (
                    userId TEXT NOT NULL PRIMARY KEY COLLATE NOCASE,
                    userName TEXT NOT NULL COLLATE NOCASE
                )
            '''
        )

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
                INSERT INTO userIds (userId, userName)
                VALUES ($1, $2)
                ON CONFLICT (userId) DO UPDATE SET userName = EXCLUDED.userName
            ''',
            userId, userName
        )

        await connection.close()

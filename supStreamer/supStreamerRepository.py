from typing import Dict, Optional, Set

try:
    import CynanBotCommon.utils as utils
    from CynanBotCommon.simpleDateTime import SimpleDateTime
    from CynanBotCommon.storage.backingDatabase import BackingDatabase
    from CynanBotCommon.storage.databaseConnection import DatabaseConnection
    from CynanBotCommon.storage.databaseType import DatabaseType
    from CynanBotCommon.supStreamer.supStreamerAction import SupStreamerAction
    from CynanBotCommon.supStreamer.supStreamerChatter import \
        SupStreamerChatter
    from CynanBotCommon.supStreamer.supStreamerRepositoryInterface import \
        SupStreamerRepositoryInterface
    from CynanBotCommon.timber.timberInterface import TimberInterface
except:
    import utils
    from simpleDateTime import SimpleDateTime
    from storage.backingDatabase import BackingDatabase
    from storage.databaseConnection import DatabaseConnection
    from storage.databaseType import DatabaseType
    from supStreamer.supStreamerAction import SupStreamerAction
    from supStreamer.supStreamerChatter import SupStreamerChatter
    from supStreamer.supStreamerRepositoryInterface import \
        SupStreamerRepositoryInterface
    from timber.timberInterface import TimberInterface


class SupStreamerRepository(SupStreamerRepositoryInterface):

    def __init__(
        self,
        backingDatabase: BackingDatabase,
        timber: TimberInterface
    ):
        if not isinstance(backingDatabase, BackingDatabase):
            raise ValueError(f'backingDatabase argument is malformed: \"{backingDatabase}\"')
        elif not isinstance(timber, TimberInterface):
            raise ValueError(f'timber argument is malformed: \"{timber}\"')

        self.__backingDatabase: BackingDatabase = backingDatabase
        self.__timber: TimberInterface = timber

        self.__cache: Dict[str, Optional[SupStreamerAction]] = dict()
        self.__isDatabaseReady: bool = False

    async def clearCaches(self):
        self.__cache.clear()
        self.__timber.log('SupStreamerRepository', 'Caches cleared')

    async def get(self, broadcasterUserId: str) -> Optional[SupStreamerAction]:
        if not utils.isValidStr(broadcasterUserId):
            raise ValueError(f'broadcasterUserId argument is malformed: \"{broadcasterUserId}\"')

        if broadcasterUserId in self.__cache:
            return self.__cache[broadcasterUserId]

        connection = await self.__getDatabaseConnection()
        records = await connection.fetchRows(
            '''
                SELECT supstreamerchatters.mostrecentsup, supstreamerchatters.userid, userids.username FROM supstreamerchatters
                INNER JOIN userids ON supstreamerchatters.twitchchannelid = userids.userid
                ORDER BY supstreamerchatters.mostrecentsup ASC
                WHERE supstreamerchatters.twitchchannelid = $1
            ''',
            broadcasterUserId
        )

        await connection.close()
        broadcasterUserName: Optional[str] = None
        chatters: Set[SupStreamerChatter] = set()

        if utils.hasItems(records):
            for record in records:
                mostRecentSup: Optional[SimpleDateTime] = None

                if utils.isValidStr(record[0]):
                    mostRecentSup = SimpleDateTime(utils.getDateTimeFromStr(mostRecentSup))

                chatters.add(SupStreamerChatter(
                    mostRecentSup = mostRecentSup,
                    userId = record[1]
                ))

                if broadcasterUserName is None:
                    broadcasterUserName = record[2]

        if utils.isValidStr(broadcasterUserName):
            action = SupStreamerAction(
                chatters = chatters,
                broadcasterUserId = broadcasterUserId,
                broadcasterUserName = broadcasterUserName
            )

        self.__cache[broadcasterUserId] = action
        return action

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
                    CREATE TABLE IF NOT EXISTS supstreamerchatters (
                        mostrecentsup text NOT NULL,
                        userid public.citext NOT NULL,
                        twitchchannelid public.citext NOT NULL
                    )
                '''
            )
        elif connection.getDatabaseType() is DatabaseType.SQLITE:
            await connection.createTableIfNotExists(
                '''
                    CREATE TABLE IF NOT EXISTS supstreamerchatters (
                        mostrecentsup TEXT NOT NULL,
                        userid TEXT NOT NULL COLLATE NOCASE,
                        twitchchannelid TEXT NOT NULL COLLATE NOCASE
                    )
                '''
            )
        else:
            raise RuntimeError(f'Encountered unexpected DatabaseType when trying to create tables: \"{connection.getDatabaseType()}\"')

        await connection.close()

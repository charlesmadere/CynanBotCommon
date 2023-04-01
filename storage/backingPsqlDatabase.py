from asyncio import AbstractEventLoop
from typing import Optional

import asyncpg

try:
    from CynanBotCommon.storage.backingDatabase import BackingDatabase
    from CynanBotCommon.storage.databaseConnection import DatabaseConnection
    from CynanBotCommon.storage.databaseType import DatabaseType
    from CynanBotCommon.storage.psqlCredentialsProvider import \
        PsqlCredentialsProvider
    from CynanBotCommon.storage.psqlDatabaseConnection import \
        PsqlDatabaseConnection
except:
    from storage.backingDatabase import BackingDatabase
    from storage.databaseConnection import DatabaseConnection
    from storage.databaseType import DatabaseType
    from storage.psqlCredentialsProvider import PsqlCredentialsProvider
    from storage.psqlDatabaseConnection import PsqlDatabaseConnection


class BackingPsqlDatabase(BackingDatabase):

    def __init__(
        self,
        eventLoop: AbstractEventLoop,
        psqlCredentialsProvider: PsqlCredentialsProvider
    ):
        if not isinstance(eventLoop, AbstractEventLoop):
            raise ValueError(f'eventLoop argument is malformed: \"{eventLoop}\"')
        elif not isinstance(psqlCredentialsProvider, PsqlCredentialsProvider):
            raise ValueError(f'psqlCredentialsProvider argument is malformed: \"{psqlCredentialsProvider}\"')

        self.__eventLoop: AbstractEventLoop = eventLoop
        self.__psqlCredentialsProvider: PsqlCredentialsProvider = psqlCredentialsProvider

        self.__connectionPool: Optional[asyncpg.Pool] = None

    async def getConnection(self) -> DatabaseConnection:
        databaseName = await self.__psqlCredentialsProvider.requireDatabaseName()
        user = await self.__psqlCredentialsProvider.requireUser()

        if self.__connectionPool is None:
            self.__connectionPool = await asyncpg.create_pool(
                database = databaseName,
                loop = self.__eventLoop,
                max_size = 100,
                user = user
            )

        connection = await self.__connectionPool.acquire()

        return PsqlDatabaseConnection(
            connection = connection,
            pool = self.__connectionPool
        )

    def getDatabaseType(self) -> DatabaseType:
        return DatabaseType.POSTGRESQL

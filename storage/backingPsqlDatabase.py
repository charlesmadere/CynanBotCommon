from asyncio import AbstractEventLoop

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

    async def getConnection(self) -> DatabaseConnection:
        databaseName = await self.__psqlCredentialsProvider.requireDatabaseName()
        user = await self.__psqlCredentialsProvider.requireUser()

        return PsqlDatabaseConnection(await asyncpg.connect(
            database = databaseName,
            loop = self.__eventLoop,
            user = user
        ))

    def getDatabaseType(self) -> DatabaseType:
        return DatabaseType.POSTGRESQL

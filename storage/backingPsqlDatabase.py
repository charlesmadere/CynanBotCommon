from asyncio import AbstractEventLoop

import asyncpg
from asyncpg import Connection

try:
    from CynanBotCommon.storage.psqlCredentialsProvider import \
        PsqlCredentialsProvider
except:
    from storage.psqlCredentialsProvider import PsqlCredentialsProvider


class BackingPsqlDatabase():

    def __init__(
        self,
        eventLoop: AbstractEventLoop,
        psqlCredentialsProvider: PsqlCredentialsProvider
    ):
        if eventLoop is None:
            raise ValueError(f'eventLoop argument is malformed: \"{eventLoop}\"')
        elif psqlCredentialsProvider is None:
            raise ValueError(f'psqlCredentialsProvider argument is malformed: \"{psqlCredentialsProvider}\"')

        self.__eventLoop: AbstractEventLoop = eventLoop
        self.__psqlCredentialsProvider: PsqlCredentialsProvider = psqlCredentialsProvider

    async def getConnection(self) -> Connection:
        database = await self.__psqlCredentialsProvider.requireDatabase()
        user = await self.__psqlCredentialsProvider.requireUser()

        return await asyncpg.connect(
            database = database,
            loop = self.__eventLoop,
            user = user
        )

from typing import Any, List, Optional

import aiosqlite

try:
    import CynanBotCommon.utils as utils
    from CynanBotCommon.storage.databaseConnection import DatabaseConnection
    from CynanBotCommon.storage.databaseType import DatabaseType
except:
    import utils
    from storage.databaseConnection import DatabaseConnection
    from storage.databaseType import DatabaseType


class SqliteDatabaseConnection(DatabaseConnection):

    def __init__(self, connection: aiosqlite.Connection):
        if not isinstance(connection, aiosqlite.Connection):
            raise ValueError(f'connection argument is malformed: \"{connection}\"')

        self.__connection: aiosqlite.Connection = connection
        self.__isClosed: bool = False

    async def close(self):
        if self.__isClosed:
            return

        self.__isClosed = True
        await self.__connection.close()

    async def execute(self, query: str, *args: Optional[Any]):
        if not utils.isValidStr(query):
            raise ValueError(f'query argument is malformed: \"{query}\"')

        self.__requireNotClosed()
        cursor = await self.__connection.execute(query, args)
        await self.__connection.commit()
        await cursor.close()

    async def fetchRow(self, query: str, *args: Optional[Any]) -> Optional[List[Any]]:
        if not utils.isValidStr(query):
            raise ValueError(f'query argument is malformed: \"{query}\"')

        self.__requireNotClosed()
        cursor = await self.__connection.execute(query, args)
        row = await cursor.fetchone()

        if not utils.hasItems(row):
            await cursor.close()
            return None

        results: List[Any] = list()
        results.extend(row)

        await cursor.close()
        return results

    async def fetchRows(self, query: str, *args: Optional[Any]) -> Optional[List[List[Any]]]:
        if not utils.isValidStr(query):
            raise ValueError(f'query argument is malformed: \"{query}\"')

        self.__requireNotClosed()
        cursor = await self.__connection.execute(query, args)
        rows = await cursor.fetchall()

        if not utils.hasItems(rows):
            await cursor.close()
            return None

        records: List[List[Any]] = list()

        for record in records:
            records.append(list(record))

        await cursor.close()
        return records

    def getDatabaseType(self) -> DatabaseType:
        return DatabaseType.SQLITE

    def isClosed(self) -> bool:
        return self.__isClosed

    def __requireNotClosed(self):
        if self.__isClosed:
            raise RuntimeError(f'This database connection has already been closed!')

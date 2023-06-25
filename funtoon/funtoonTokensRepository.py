import json
import os
from typing import Dict, Optional

import aiofiles
import aiofiles.ospath

try:
    import CynanBotCommon.utils as utils
    from CynanBotCommon.funtoon.exceptions import NoFuntoonTokenException
    from CynanBotCommon.storage.backingDatabase import BackingDatabase
    from CynanBotCommon.storage.databaseConnection import DatabaseConnection
    from CynanBotCommon.storage.databaseType import DatabaseType
    from CynanBotCommon.timber.timber import Timber
except:
    import utils
    from funtoon.exceptions import NoFuntoonTokenException
    from storage.backingDatabase import BackingDatabase
    from storage.databaseConnection import DatabaseConnection
    from storage.databaseType import DatabaseType
    from timber.timber import Timber


class FuntoonTokensRepository():

    def __init__(
        self,
        backingDatabase: BackingDatabase,
        timber: Timber,
        seedFile: Optional[str] = f'CynanBotCommon/funtoon/funtoonTokensRepositorySeedFile.json'
    ):
        if not isinstance(backingDatabase, BackingDatabase):
            raise ValueError(f'backingDatabase argument is malformed: \"{backingDatabase}\"')
        elif not isinstance(timber, Timber):
            raise ValueError(f'timber argument is malformed: \"{timber}\"')
        elif seedFile is not None and not isinstance(seedFile, str):
            raise ValueError(f'seedFile argument is malformed: \"{seedFile}\"')

        self.__backingDatabase: BackingDatabase = backingDatabase
        self.__timber: Timber = timber
        self.__seedFile: Optional[str] = seedFile

        self.__isDatabaseReady: bool = False
        self.__cache: Dict[str, str] = dict()

    async def clearCaches(self):
        self.__cache.clear()

    async def __consumeSeedFile(self):
        seedFile = self.__seedFile

        if not utils.isValidStr(seedFile):
            return

        self.__seedFile = None

        if not await aiofiles.ospath.exists(seedFile):
            self.__timber.log('FuntoonTokensRepository', f'Seed file (\"{seedFile}\") does not exist')
            return

        async with aiofiles.open(seedFile, mode = 'r') as file:
            data = await file.read()
            jsonContents: Optional[Dict[str, str]] = json.loads(data)

        # I don't believe there is an aiofiles version of this call at this time (June 23rd, 2023).
        os.remove(seedFile)

        if not utils.hasItems(jsonContents):
            self.__timber.log('FuntoonTokensRepository', f'Seed file (\"{seedFile}\") is empty')
            return

        self.__timber.log('FuntoonTokensRepository', f'Reading in seed file \"{seedFile}\"...')

        for twitchChannel, token in jsonContents.items():
            await self.setToken(
                twitchChannel = twitchChannel,
                token = token
            )

        self.__timber.log('FuntoonTokensRepository', f'Finished reading in seed file \"{seedFile}\"')

    async def __getDatabaseConnection(self) -> DatabaseConnection:
        await self.__initDatabaseTable()
        return await self.__backingDatabase.getConnection()

    async def getToken(self, twitchChannel: str) -> Optional[str]:
        if not utils.isValidStr(twitchChannel):
            raise ValueError(f'twitchChannel argument is malformed: \"{twitchChannel}\"')

        if twitchChannel.lower() in self.__cache:
            return self.__cache[twitchChannel.lower()]

        connection = await self.__getDatabaseConnection()
        record = await connection.fetchRow(
            '''
                SELECT token FROM funtoontokens
                WHERE twitchchannel = $1
                LIMIT 1
            ''',
            twitchChannel
        )

        token: Optional[str] = None

        if utils.hasItems(record):
            token = record[0]

        self.__cache[twitchChannel.lower()] = token
        await connection.close()

        return token

    async def __initDatabaseTable(self):
        if self.__isDatabaseReady:
            return

        self.__isDatabaseReady = True
        connection = await self.__backingDatabase.getConnection()

        if connection.getDatabaseType() is DatabaseType.POSTGRESQL:
            await connection.createTableIfNotExists(
                '''
                    CREATE TABLE IF NOT EXISTS funtoontokens (
                        token text NOT NULL,
                        twitchchannel public.citext NOT NULL PRIMARY KEY
                    )
                '''
            )
        elif connection.getDatabaseType() is DatabaseType.SQLITE:
            await connection.createTableIfNotExists(
                '''
                    CREATE TABLE IF NOT EXISTS funtoontokens (
                        token TEXT NOT NULL,
                        twitchchannel TEXT NOT NULL PRIMARY KEY COLLATE NOCASE
                    )
                '''
            )
        else:
            raise RuntimeError(f'Encountered unexpected DatabaseType when trying to create tables: \"{connection.getDatabaseType()}\"')

        await connection.close()
        await self.__consumeSeedFile()

    async def requireToken(self, twitchChannel: str) -> str:
        if not utils.isValidStr(twitchChannel):
            raise ValueError(f'twitchChannel argument is malformed: \"{twitchChannel}\"')

        token = await self.getToken(twitchChannel)

        if not utils.isValidStr(token):
            raise NoFuntoonTokenException(f'token for twitchChannel \"{twitchChannel}\" is missing/unavailable')

        return token

    async def setToken(self, twitchChannel: str, token: Optional[str]):
        if not utils.isValidStr(twitchChannel):
            raise ValueError(f'twitchChannel argument is malformed: \"{twitchChannel}\"')
        elif token is not None and not isinstance(token, str):
            raise ValueError(f'token argument is malformed: \"{token}\"')

        connection = await self.__getDatabaseConnection()

        if utils.isValidStr(token):
            await connection.execute(
                '''
                    INSERT INTO funtoontokens (token, twitchchannel)
                    VALUES ($1, $2)
                    ON CONFLICT (twitchchannel) DO UPDATE SET token = EXCLUDED.token
                ''',
                token, twitchChannel
            )

            self.__cache[twitchChannel.lower()] = token
            self.__timber.log('FuntoonTokensRepository', f'Funtoon token for \"{twitchChannel}\" has been updated (\"{token}\")')
        else:
            await connection.execute(
                '''
                    DELETE FROM funtoontokens
                    WHERE twitchchannel = $1
                ''',
                twitchChannel
            )

            self.__cache[twitchChannel.lower()] = None
            self.__timber.log('FuntoonTokensRepository', f'Funtoon token for \"{twitchChannel}\" has been deleted')

        await connection.close()

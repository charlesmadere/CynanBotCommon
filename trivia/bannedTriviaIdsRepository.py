from typing import Optional

from aiosqlite import Connection

try:
    import CynanBotCommon.utils as utils
    from CynanBotCommon.backingDatabase import BackingDatabase
    from CynanBotCommon.timber.timber import Timber
    from CynanBotCommon.trivia.triviaSettingsRepository import \
        TriviaSettingsRepository
    from CynanBotCommon.trivia.triviaSource import TriviaSource
except:
    import utils
    from backingDatabase import BackingDatabase
    from timber.timber import Timber

    from trivia.triviaSettingsRepository import TriviaSettingsRepository
    from trivia.triviaSource import TriviaSource


class BannedTriviaIdsRepository():

    def __init__(
        self,
        backingDatabase: BackingDatabase,
        timber: Timber,
        triviaSettingsRepository: TriviaSettingsRepository
    ):
        if backingDatabase is None:
            raise ValueError(f'backingDatabase argument is malformed: \"{backingDatabase}\"')
        elif timber is None:
            raise ValueError(f'timber argument is malformed: \"{timber}\"')
        elif triviaSettingsRepository is None:
            raise ValueError(f'triviaSettingsRepository argument is malformed: \"{triviaSettingsRepository}\"')

        self.__backingDatabase: BackingDatabase = backingDatabase
        self.__timber: Timber = timber
        self.__triviaSettingsRepository: TriviaSettingsRepository = triviaSettingsRepository

        self.__isDatabaseReady: bool = False

    async def ban(self, triviaId: str, triviaSource: TriviaSource):
        if not utils.isValidStr(triviaId):
            raise ValueError(f'triviaId argument is malformed: \"{triviaId}\"')
        elif triviaSource is None:
            raise ValueError(f'triviaSource argument is malformed: \"{triviaSource}\"')

        if await self.__triviaSettingsRepository.isDebugLoggingEnabled():
            self.__timber.log('BannedTriviaIdsRepository', f'Banning trivia question (triviaId=\"{triviaId}\", triviaSource=\"{triviaSource}\")...')

        await self.__banQuestion(triviaId, triviaSource)

    async def __banQuestion(self, triviaId: str, triviaSource: TriviaSource):
        if not utils.isValidStr(triviaId):
            raise ValueError(f'triviaId argument is malformed: \"{triviaId}\"')
        elif triviaSource is None:
            raise ValueError(f'triviaSource argument is malformed: \"{triviaSource}\"')

        connection = await self.__getDatabaseConnection()
        cursor = await connection.execute(
            '''
                INSERT OR IGNORE INTO bannedTriviaIds (triviaId, triviaSource)
                VALUES (?, ?)
            ''',
            ( triviaId, triviaSource.toStr() )
        )

        await connection.commit()
        await cursor.close()
        await connection.close()

    async def __getDatabaseConnection(self) -> Connection:
        await self.__initDatabaseTable()
        return await self.__backingDatabase.getConnection()

    async def __initDatabaseTable(self):
        if self.__isDatabaseReady:
            return

        self.__isDatabaseReady = True

        connection = await self.__backingDatabase.getConnection()
        cursor = await connection.execute(
            '''
                CREATE TABLE IF NOT EXISTS bannedTriviaIds (
                    triviaId TEXT NOT NULL COLLATE NOCASE,
                    triviaSource TEXT NOT NULL COLLATE NOCASE,
                    PRIMARY KEY (triviaId, triviaSource)
                )
            '''
        )

        await connection.commit()
        await cursor.close()
        await connection.close()

    async def isBanned(self, triviaSource: TriviaSource, triviaId: str) -> bool:
        if triviaSource is None:
            raise ValueError(f'triviaSource argument is malformed: \"{triviaSource}\"')
        elif not utils.isValidStr(triviaId):
            raise ValueError(f'triviaId argument is malformed: \"{triviaId}\"')

        if not await self.__triviaSettingsRepository.isBanListEnabled():
            return False

        connection = await self.__getDatabaseConnection()
        cursor = await connection.execute(
            '''
                SELECT COUNT(1) FROM bannedTriviaIds
                WHERE triviaId = ? AND triviaSource = ?
            ''',
            ( triviaId, triviaSource.toStr() )
        )

        row = await cursor.fetchone()
        count: Optional[int] = None

        if row is not None:
            count = row[0]

        await cursor.close()
        await connection.close()

        if not utils.isValidNum(count) or count < 1:
            return False

        if await self.__triviaSettingsRepository.isDebugLoggingEnabled():
            self.__timber.log('BannedTriviaIdsRepository', f'Encountered banned trivia ID with count of {count} (triviaId=\"{triviaId}\", triviaSource=\"{triviaSource}\")')

        return True

    async def unban(self, triviaId: str, triviaSource: TriviaSource):
        if not utils.isValidStr(triviaId):
            raise ValueError(f'triviaId argument is malformed: \"{triviaId}\"')
        elif triviaSource is None:
            raise ValueError(f'triviaSource argument is malformed: \"{triviaSource}\"')

        if await self.__triviaSettingsRepository.isDebugLoggingEnabled():
            self.__timber.log('BannedTriviaIdsRepository', f'Unbanning trivia question (triviaId=\"{triviaId}\", triviaSource=\"{triviaSource}\")...')

        connection = await self.__getDatabaseConnection()
        cursor = await connection.execute(
            '''
                DELETE FROM bannedTriviaIds
                WHERE triviaId = ? AND triviaSource = ?
            ''',
            ( triviaId, triviaSource.toStr() )
        )

        await connection.commit()
        await cursor.close()
        await connection.close()

from typing import Optional, Set

try:
    import CynanBotCommon.utils as utils
    from CynanBotCommon.language.addAutoWordOfTheDayLanguageResult import \
        AddAutoWordOfTheDayLanguageResult
    from CynanBotCommon.language.autoWordOfTheDayRepositoryInterface import \
        AutoWordOfTheDayRepositoryInterface
    from CynanBotCommon.language.languageEntry import LanguageEntry
    from CynanBotCommon.language.languagesRepository import LanguagesRepository
    from CynanBotCommon.language.removeAutoWordOfTheDayLanguageResult import \
        RemoveAutoWordOfTheDayLanguageResult
    from CynanBotCommon.storage.backingDatabase import BackingDatabase
    from CynanBotCommon.storage.databaseConnection import DatabaseConnection
    from CynanBotCommon.storage.databaseType import DatabaseType
    from CynanBotCommon.timber.timberInterface import TimberInterface
except:
    import utils
    from language.addAutoWordOfTheDayLanguageResult import \
        AddAutoWordOfTheDayLanguageResult
    from language.autoWordOfTheDayRepositoryInterface import \
        AutoWordOfTheDayRepositoryInterface
    from language.languageEntry import LanguageEntry
    from language.languagesRepository import LanguagesRepository
    from language.removeAutoWordOfTheDayLanguageResult import \
        RemoveAutoWordOfTheDayLanguageResult
    from storage.backingDatabase import BackingDatabase
    from storage.databaseConnection import DatabaseConnection
    from storage.databaseType import DatabaseType
    from timber.timberInterface import TimberInterface


class AutoWordOfTheDayRepository(AutoWordOfTheDayRepositoryInterface):

    def __init__(
        self,
        backingDatabase: BackingDatabase,
        languagesRepository: LanguagesRepository,
        timber: TimberInterface
    ):
        if not isinstance(backingDatabase, BackingDatabase):
            raise ValueError(f'backingDatabase argument is malformed: \"{backingDatabase}\"')
        elif not isinstance(languagesRepository, LanguagesRepository):
            raise ValueError(f'languagesRepository argument is malformed: \"{languagesRepository}\"')
        elif not isinstance(timber, TimberInterface):
            raise ValueError(f'timber argument is malformed: \"{timber}\"')

        self.__backingDatabase: BackingDatabase = backingDatabase
        self.__languagesRepository: LanguagesRepository = languagesRepository
        self.__timber: TimberInterface = timber

        self.__isDatabaseReady: bool = False

    async def addAutoLanguageEntry(
        self,
        languageEntry: LanguageEntry,
        twitchChannel: str
    ) -> AddAutoWordOfTheDayLanguageResult:
        if not isinstance(languageEntry, LanguageEntry):
            raise ValueError(f'languageEntry argument is malformed: \"{languageEntry}\"')
        elif not utils.isValidStr(twitchChannel):
            raise ValueError(f'twitchChannel argument is malformed: \"{twitchChannel}\"')

        if not languageEntry.hasWotdApiCode():
            self.__timber.log('AutoWordOfTheDayRepository', f'languageEntry \"{languageEntry}\" does not have a WOTD API code and therefore can\'t be added')
            return AddAutoWordOfTheDayLanguageResult.ERROR

        connection = await self.__getDatabaseConnection()
        record = await connection.execute(
            '''
                SELECT COUNT(1) FROM autowordofthedaylanguages
                WHERE twitchchannel = $1 AND wotdapicode = $2
                LIMIT 1
            ''',
            twitchChannel, languageEntry.getWotdApiCode()
        )

        count: Optional[int] = None
        if utils.hasItems(record):
            count = record[0]

        if utils.isValidInt(count) and count >= 1:
            await connection.close()
            self.__timber.log('AutoWordOfTheDayRepository', f'Tried to add languageEntry=\"{languageEntry}\" as an auto word of the day language for \"{twitchChannel}\", but this language has already been added as one')
            return AddAutoWordOfTheDayLanguageResult.ALREADY_EXISTS

        await connection.execute(
            '''
                INSERT INTO autowordofthedaylanguages (twitchchannel, wotdapicode)
                VALUES ($1, $2)
                ON CONFLICT (twitchchannel, wotdapicode) DO NOTHING
            ''',
            twitchChannel, languageEntry.getWotdApiCode()
        )

        await connection.close()
        self.__timber.log('AutoWordOfTheDayRepository', f'Added languageEntry=\"{languageEntry}\" as an auto word of the day language for \"{twitchChannel}\"')

        return AddAutoWordOfTheDayLanguageResult.ADDED

    async def getAutoLanguageEntries(
        self,
        twitchChannel: str
    ) -> Set[LanguageEntry]:
        if not utils.isValidStr(twitchChannel):
            raise ValueError(f'twitchChannel argument is malformed: \"{twitchChannel}\"')

        connection = await self.__getDatabaseConnection()
        records = await connection.fetchRows(
            '''
                SELECT wotdapicode FROM autowordofthedaylanguages
                WHERE twitchchannel = $1
                ORDER BY wotdapicode ASC
            ''',
            twitchChannel
        )

        await connection.close()
        languageEntries: Set[LanguageEntry] = set()

        if not utils.hasItems(records):
            return languageEntries

        for record in records:
            languageEntry = await self.__languagesRepository.requireLanguageForWotdApiCode(record[0])
            languageEntries.add(languageEntry)

        return languageEntries

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
                    CREATE TABLE IF NOT EXISTS autowordofthedaylanguages (
                        twitchchannel public.citext NOT NULL,
                        wotdapicode public.citext NOT NULL,
                        PRIMARY KEY (twitchchannel, wotdapicode)
                    )
                '''
            )
        elif connection.getDatabaseType() is DatabaseType.SQLITE:
            await connection.createTableIfNotExists(
                '''
                    CREATE TABLE IF NOT EXISTS autowordofthedaylanguages (
                        twitchchannel TEXT NOT NULL COLLATE NOCASE,
                        wotdapicode TEXT NOT NULL COLLATE NOCASE,
                        PRIMARY KEY (twitchchannel, wotdapicode)
                    )
                '''
            )
        else:
            raise RuntimeError(f'Encountered unexpected DatabaseType when trying to create tables: \"{connection.getDatabaseType()}\"')

        await connection.close()

    async def removeAutoLanguageEntry(
        self,
        languageEntry: LanguageEntry,
        twitchChannel: str
    ) -> RemoveAutoWordOfTheDayLanguageResult:
        if not isinstance(languageEntry, LanguageEntry):
            raise ValueError(f'languageEntry argument is malformed: \"{languageEntry}\"')
        elif not utils.isValidStr(twitchChannel):
            raise ValueError(f'twitchChannel argument is malformed: \"{twitchChannel}\"')

        if not languageEntry.hasWotdApiCode():
            self.__timber.log('AutoWordOfTheDayRepository', f'languageEntry \"{languageEntry}\" does not have a WOTD API code and therefore can\'t be removed')
            return RemoveAutoWordOfTheDayLanguageResult.ERROR

        connection = await self.__backingDatabase.getConnection()
        await connection.execute(
            '''
                DELETE FROM autowordofthedaylanguages
                WHERE twitchchannel = $1 AND wotdapicode = $2
            ''',
            twitchChannel, languageEntry.getWotdApiCode()
        )

        await connection.close()
        self.__timber.log('AutoWordOfTheDayRepository', f'Removed languageEntry=\"{languageEntry}\" as an auto word of the day language for \"{twitchChannel}\"')

        return RemoveAutoWordOfTheDayLanguageResult.REMOVED

from datetime import datetime, timedelta, timezone
from typing import Optional

try:
    import CynanBotCommon.utils as utils
    from CynanBotCommon.storage.backingDatabase import BackingDatabase
    from CynanBotCommon.storage.databaseConnection import DatabaseConnection
    from CynanBotCommon.storage.databaseType import DatabaseType
    from CynanBotCommon.timber.timber import Timber
    from CynanBotCommon.trivia.absTriviaQuestion import AbsTriviaQuestion
    from CynanBotCommon.trivia.triviaContentCode import TriviaContentCode
    from CynanBotCommon.trivia.triviaQuestionReference import \
        TriviaQuestionReference
    from CynanBotCommon.trivia.triviaSettingsRepository import \
        TriviaSettingsRepository
    from CynanBotCommon.trivia.triviaSource import TriviaSource
except:
    import utils
    from storage.backingDatabase import BackingDatabase
    from storage.databaseConnection import DatabaseConnection
    from storage.databaseType import DatabaseType
    from timber.timber import Timber
    from trivia.absTriviaQuestion import AbsTriviaQuestion
    from trivia.triviaContentCode import TriviaContentCode
    from trivia.triviaQuestionReference import TriviaQuestionReference
    from trivia.triviaSettingsRepository import TriviaSettingsRepository
    from trivia.triviaSource import TriviaSource


class TriviaHistoryRepository():

    def __init__(
        self,
        backingDatabase: BackingDatabase,
        timber: Timber,
        triviaSettingsRepository: TriviaSettingsRepository,
        timeZone: timezone = timezone.utc
    ):
        if not isinstance(backingDatabase, BackingDatabase):
            raise ValueError(f'backingDatabase argument is malformed: \"{backingDatabase}\"')
        elif not isinstance(timber, Timber):
            raise ValueError(f'timber argument is malformed: \"{timber}\"')
        elif not isinstance(triviaSettingsRepository, TriviaSettingsRepository):
            raise ValueError(f'triviaSettingsRepository argument is malformed: \"{triviaSettingsRepository}\"')
        elif not isinstance(timeZone, timezone):
            raise ValueError(f'timeZone argument is malformed: \"{timeZone}\"')

        self.__backingDatabase: BackingDatabase = backingDatabase
        self.__timber: Timber = timber
        self.__triviaSettingsRepository: TriviaSettingsRepository = triviaSettingsRepository
        self.__timeZone: timezone = timeZone

        self.__isDatabaseReady: bool = False

    async def __getDatabaseConnection(self) -> DatabaseConnection:
        await self.__initDatabaseTable()
        return await self.__backingDatabase.getConnection()

    async def getMostRecentTriviaQuestionDetails(
        self,
        emote: str,
        twitchChannel: str
    ) -> Optional[TriviaQuestionReference]:
        if not utils.isValidStr(emote):
            raise ValueError(f'emote argument is malformed: \"{emote}\"')
        elif not utils.isValidStr(twitchChannel):
            raise ValueError(f'twitchChannel argument is malformed: \"{twitchChannel}\"')

        connection = await self.__getDatabaseConnection()
        record = await connection.fetchRow(
            '''
                SELECT emote, triviaid, triviasource FROM triviahistory
                WHERE emote IS NOT NULL AND emote = $1 AND twitchchannel = $2
                ORDER BY datetime DESC
                LIMIT 1
            ''',
            emote, twitchChannel
        )

        triviaQuestionReference: Optional[TriviaQuestionReference] = None

        if utils.hasItems(record):
            triviaQuestionReference = TriviaQuestionReference(
                emote = record[0],
                triviaId = record[1],
                twitchChannel = twitchChannel,
                triviaSource = TriviaSource.fromStr(record[2])
            )

        await connection.close()
        return triviaQuestionReference

    async def __initDatabaseTable(self):
        if self.__isDatabaseReady:
            return

        self.__isDatabaseReady = True
        connection = await self.__backingDatabase.getConnection()

        if connection.getDatabaseType() is DatabaseType.POSTGRESQL:
            await connection.createTableIfNotExists(
                '''
                    CREATE TABLE IF NOT EXISTS triviahistory (
                        datetime text NOT NULL,
                        emote text NOT NULL,
                        triviaid public.citext NOT NULL,
                        triviasource public.citext NOT NULL,
                        twitchchannel public.citext NOT NULL,
                        triviaid public.citext NOT NULL,
                        PRIMARY KEY (triviaid, triviasource, twitchchannel)
                    )
                '''
            )
        elif connection.getDatabaseType() is DatabaseType.SQLITE:
            await connection.createTableIfNotExists(
                '''
                    CREATE TABLE IF NOT EXISTS triviahistory (
                        datetime TEXT NOT NULL,
                        emote TEXT NOT NULL,
                        triviaid TEXT NOT NULL COLLATE NOCASE,
                        triviasource TEXT NOT NULL COLLATE NOCASE,
                        twitchchannel TEXT NOT NULL COLLATE NOCASE,
                        PRIMARY KEY (triviaid, triviasource, twitchchannel)
                    )
                '''
            )
        else:
            raise RuntimeError(f'Encountered unexpected DatabaseType when trying to create tables: \"{connection.getDatabaseType()}\"')

        await connection.close()

    async def verify(
        self,
        question: AbsTriviaQuestion,
        twitchChannel: str
    ) -> TriviaContentCode:
        if not isinstance(question, AbsTriviaQuestion):
            raise ValueError(f'question argument is malformed: \"{question}\"')
        elif not utils.isValidStr(twitchChannel):
            raise ValueError(f'twitchChannel argument is malformed: \"{twitchChannel}\"')

        emote = question.getEmote()
        triviaId = question.getTriviaId()
        triviaSource = question.getTriviaSource().toStr()

        connection = await self.__getDatabaseConnection()
        record = await connection.fetchRow(
            '''
                SELECT datetime FROM triviahistory
                WHERE triviaid = $1 AND triviasource = $2 AND twitchchannel = $3
                LIMIT 1
            ''',
            triviaId, triviaSource, twitchChannel
        )

        nowDateTime = datetime.now(self.__timeZone)
        nowDateTimeStr = nowDateTime.isoformat()

        if not utils.hasItems(record):
            await connection.execute(
                '''
                    INSERT INTO triviahistory (datetime, emote, triviaid, triviasource, twitchchannel)
                    VALUES ($1, $2, $3, $4, $5)
                ''',
                nowDateTimeStr, emote, triviaId, triviaSource, twitchChannel
            )

            await connection.close()
            return TriviaContentCode.OK

        questionDateTimeStr: str = record[0]
        questionDateTime = datetime.fromisoformat(questionDateTimeStr)
        minimumTimeDelta = timedelta(days = await self.__triviaSettingsRepository.getMinDaysBeforeRepeatQuestion())
        isDebugLoggingEnabled = await self.__triviaSettingsRepository.isDebugLoggingEnabled()

        if questionDateTime + minimumTimeDelta >= nowDateTime:
            if isDebugLoggingEnabled:
                self.__timber.log('TriviaHistoryRepository', f'Encountered duplicate triviaHistory entry that is within the window of being a repeat (now=\"{nowDateTimeStr}\" db=\"{questionDateTimeStr}\" triviaId=\"{triviaId}\" triviaSource=\"{triviaSource}\" twitchChannel=\"{twitchChannel}\"')

            await connection.close()
            return TriviaContentCode.REPEAT

        await connection.execute(
            '''
                UPDATE triviahistory
                SET datetime = $1, emote = $2
                WHERE triviaid = $3 AND triviasource = $4 AND twitchchannel = $5
            ''',
            nowDateTimeStr, emote, triviaId, triviaSource, twitchChannel
        )

        if isDebugLoggingEnabled:
            self.__timber.log('TriviaHistoryRepository', f'Updated triviaHistory entry to {nowDateTimeStr} from {questionDateTimeStr} (triviaId=\"{triviaId}\" triviaSource=\"{triviaSource}\" twitchChannel=\"{twitchChannel}\")')

        await connection.close()
        return TriviaContentCode.OK

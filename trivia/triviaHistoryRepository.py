from datetime import datetime, timedelta, timezone
from typing import Optional

from aiosqlite import Connection

try:
    import CynanBotCommon.utils as utils
    from CynanBotCommon.backingDatabase import BackingDatabase
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
    from backingDatabase import BackingDatabase
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

    async def __getDatabaseConnection(self) -> Connection:
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
        cursor = await connection.execute(
            '''
                SELECT emote, triviaId, triviaSource FROM triviaHistory
                WHERE emote IS NOT NULL AND emote = ? AND twitchChannel = ?
                ORDER BY datetime DESC
                LIMIT 1
            ''',
            ( emote, twitchChannel )
        )

        row = await cursor.fetchone()
        triviaQuestionReference: TriviaQuestionReference = None

        if row is not None:
            triviaQuestionReference = TriviaQuestionReference(
                emote = row[0],
                triviaId = row[1],
                twitchChannel = twitchChannel,
                triviaSource = TriviaSource.fromStr(row[2])
            )

        await cursor.close()
        await connection.close()
        return triviaQuestionReference

    async def __initDatabaseTable(self):
        if self.__isDatabaseReady:
            return

        self.__isDatabaseReady = True

        connection = await self.__backingDatabase.getConnection()
        cursor = await connection.execute(
            '''
                CREATE TABLE IF NOT EXISTS triviaHistory (
                    datetime TEXT NOT NULL,
                    emote TEXT NOT NULL,
                    triviaId TEXT NOT NULL COLLATE NOCASE,
                    triviaSource TEXT NOT NULL COLLATE NOCASE,
                    twitchChannel TEXT NOT NULL COLLATE NOCASE,
                    PRIMARY KEY (triviaId, triviaSource, twitchChannel)
                )
            '''
        )

        await connection.commit()
        await cursor.close()
        await connection.close()

    async def verify(
        self,
        question: AbsTriviaQuestion,
        twitchChannel: str
    ) -> TriviaContentCode:
        if question is None:
            raise ValueError(f'question argument is malformed: \"{question}\"')
        elif not utils.isValidStr(twitchChannel):
            raise ValueError(f'twitchChannel argument is malformed: \"{twitchChannel}\"')

        emote = question.getEmote()
        triviaId = question.getTriviaId()
        triviaSource = question.getTriviaSource().toStr()

        connection = await self.__getDatabaseConnection()
        cursor = await connection.execute(
            '''
                SELECT datetime FROM triviaHistory
                WHERE triviaId = ? AND triviaSource = ? AND twitchChannel = ?
            ''',
            ( triviaId, triviaSource, twitchChannel )
        )

        row = await cursor.fetchone()
        nowDateTime = datetime.now(timezone.utc)
        nowDateTimeStr = nowDateTime.isoformat()

        if row is None:
            await connection.execute(
                '''
                    INSERT INTO triviaHistory (datetime, emote, triviaId, triviaSource, twitchChannel)
                    VALUES (?, ?, ?, ?, ?)
                ''',
                ( nowDateTimeStr, emote, triviaId, triviaSource, twitchChannel )
            )

            await connection.commit()
            await cursor.close()
            await connection.close()
            return TriviaContentCode.OK

        questionDateTimeStr: str = row[0]
        questionDateTime = datetime.fromisoformat(questionDateTimeStr)
        await cursor.close()

        minimumTimeDelta = timedelta(days = await self.__triviaSettingsRepository.getMinDaysBeforeRepeatQuestion())
        isDebugLoggingEnabled = await self.__triviaSettingsRepository.isDebugLoggingEnabled()

        if questionDateTime + minimumTimeDelta >= nowDateTime:
            if isDebugLoggingEnabled:
                self.__timber.log('TriviaHistoryRepository', f'Encountered duplicate triviaHistory entry for triviaId:{triviaId} triviaSource:{triviaSource} twitchChannel:{twitchChannel} that is within the window of being a repeat (now:{nowDateTimeStr}) (db:{questionDateTimeStr})')

            await connection.close()
            return TriviaContentCode.REPEAT

        await connection.execute(
            '''
                UPDATE triviaHistory
                SET datetime = ?, emote = ?
                WHERE triviaId = ? AND triviaSource = ? AND twitchChannel = ?
            ''',
            ( nowDateTimeStr, emote, triviaId, triviaSource, twitchChannel )
        )

        if isDebugLoggingEnabled:
            self.__timber.log('TriviaHistoryRepository', f'Updated triviaHistory entry for triviaId:{triviaId} triviaSource:{triviaSource} twitchChannel:{twitchChannel} to {nowDateTimeStr} from {questionDateTimeStr}')

        await connection.commit()
        await connection.close()
        return TriviaContentCode.OK

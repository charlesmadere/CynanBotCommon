from datetime import datetime, timedelta, timezone

try:
    import CynanBotCommon.utils as utils
    from CynanBotCommon.backingDatabase import BackingDatabase
    from CynanBotCommon.trivia.absTriviaQuestion import AbsTriviaQuestion
    from CynanBotCommon.trivia.triviaContentCode import TriviaContentCode
except:
    import utils
    from backingDatabase import BackingDatabase

    from trivia.absTriviaQuestion import AbsTriviaQuestion
    from trivia.triviaContentCode import TriviaContentCode


class TriviaHistoryRepository():

    def __init__(
        self,
        backingDatabase: BackingDatabase,
        minimumTimeDelta: timedelta = timedelta(weeks = 1)
    ):
        if backingDatabase is None:
            raise ValueError(f'backingDatabase argument is malformed: \"{backingDatabase}\"')
        elif minimumTimeDelta is None:
            raise ValueError(f'minimumTimeDelta argument is malformed: \"{minimumTimeDelta}\"')

        self.__backingDatabase: BackingDatabase = backingDatabase
        self.__minimumTimeDelta: timedelta = minimumTimeDelta

        self.__initDatabaseTable()

    def __initDatabaseTable(self):
        connection = self.__backingDatabase.getConnection()
        connection.execute(
            '''
                CREATE TABLE IF NOT EXISTS triviaHistory (
                    datetime TEXT NOT NULL,
                    triviaId TEXT NOT NULL COLLATE NOCASE,
                    triviaSource TEXT NOT NULL COLLATE NOCASE,
                    twitchChannel TEXT NOT NULL COLLATE NOCASE,
                    PRIMARY KEY (triviaId, triviaSource, twitchChannel)
                )
            '''
        )

        connection.commit()

    def verify(self, question: AbsTriviaQuestion, twitchChannel: str) -> TriviaContentCode:
        if not utils.isValidStr(twitchChannel):
            raise ValueError(f'twitchChannel argument is malformed: \"{twitchChannel}\"')

        if question is None:
            return TriviaContentCode.IS_NONE

        connection = self.__backingDatabase.getConnection()
        cursor = connection.cursor()
        cursor.execute(
            '''
                SELECT datetime FROM triviaHistory
                WHERE triviaId = ? AND triviaSource = ? AND twitchChannel = ?
            ''',
            ( question.getTriviaId(), question.getTriviaSource().toStr(), twitchChannel )
        )

        row = cursor.fetchone()
        nowDateTime = datetime.now(timezone.utc)

        if row is None:
            nowDateTimeStr = utils.getStrFromDateTime(nowDateTime)

            cursor.execute(
                '''
                    INSERT INTO triviaHistory (datetime, triviaId, triviaSource, twitchChannel)
                    VALUES (?, ?, ?, ?)
                ''',
                ( nowDateTimeStr, question.getTriviaId(), question.getTriviaSource().toStr(), twitchChannel )
            )

            connection.commit()
            cursor.close()
            return TriviaContentCode.OK

        questionDateTime = utils.getDateTimeFromStr(row[0])
        cursor.close()

        if questionDateTime + self.__minimumTimeDelta >= nowDateTime:
            return TriviaContentCode.REPEAT
        else:
            return TriviaContentCode.OK

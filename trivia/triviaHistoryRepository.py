from datetime import datetime, timedelta

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
        minimumTimeWindow: timedelta = timedelta(weeks = 1)
    ):
        if backingDatabase is None:
            raise ValueError(f'backingDatabase argument is malformed: \"{backingDatabase}\"')
        elif minimumTimeWindow is None:
            raise ValueError(f'minimumTimeWindow argument is malformed: \"{minimumTimeWindow}\"')

        self.__backingDatabase: BackingDatabase = backingDatabase
        self.__minimumTimeWindow: timedelta = minimumTimeWindow

        self.__initDatabaseTable()

    def __initDatabaseTable(self):
        connection = self.__backingDatabase.getConnection()
        connection.execute(
            '''
                CREATE TABLE IF NOT EXISTS triviaHistory (
                    datetime TEXT NOT NULL,
                    triviaId TEXT NOT NULL COLLATE NOCASE,
                    triviaSource TEXT NOT NULL COLLATE NOCASE,
                    PRIMARY KEY (triviaId, triviaSource)
                )
            '''
        )

        connection.commit()

    def verify(self, question: AbsTriviaQuestion) -> TriviaContentCode:
        if question is None:
            return TriviaContentCode.IS_NONE



        return TriviaContentCode.OK

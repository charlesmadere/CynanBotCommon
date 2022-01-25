try:
    import CynanBotCommon.utils as utils
    from CynanBotCommon.backingDatabase import BackingDatabase
    from CynanBotCommon.trivia.triviaScoreResult import TriviaScoreResult
except:
    import utils
    from backingDatabase import BackingDatabase

    from trivia.triviaScoreResult import TriviaScoreResult


class TriviaScoreRepository():

    def __init__(self, backingDatabase: BackingDatabase):
        if backingDatabase is None:
            raise ValueError(f'backingDatabase argument is malformed: \"{backingDatabase}\"')

        self.__backingDatabase: BackingDatabase = backingDatabase

        connection = backingDatabase.getConnection()
        connection.execute(
            '''
                CREATE TABLE IF NOT EXISTS triviaScores (
                    streak INTEGER NOT NULL DEFAULT 0,
                    totalLosses INTEGER NOT NULL DEFAULT 0,
                    totalWins INTEGER NOT NULL DEFAULT 0,
                    twitchChannel TEXT NOT NULL COLLATE NOCASE,
                    userId TEXT NOT NULL COLLATE NOCASE,
                    PRIMARY KEY (twitchChannel, userId)
                )
            '''
        )

        connection.commit()

    def fetchTriviaScore(
        self,
        twitchChannel: str,
        userId: str
    ) -> TriviaScoreResult:
        if not utils.isValidStr(twitchChannel):
            raise ValueError(f'twitchChannel argument is malformed: \"{twitchChannel}\"')
        elif not utils.isValidStr(userId):
            raise ValueError(f'userId argument is malformed: \"{userId}\"')
        elif userId == '0':
            raise ValueError(f'userId argument is an illegal value: \"{userId}\"')

        connection = self.__backingDatabase.getConnection()
        cursor = connection.cursor()
        cursor.execute(
            '''
                SELECT streak, totalLosses, totalWins, twitchChannel, userId FROM triviaScores
                WHERE twitchChannel = ? AND userId = ?
            ''',
            ( twitchChannel, userId )
        )

        row = cursor.fetchone()

        if row is not None:
            result = TriviaScoreResult(
                streak = row[0],
                totalLosses = row[1],
                totalWins = row[2],
                twitchChannel = row[3],
                userId = row[4]
            )

            cursor.close()
            return result

        cursor.execute(
            '''
                INSERT INTO triviaScores (streak, totalLosses, totalWins, twitchChannel, userId)
                VALUES (?, ?, ?, ?, ?)
            ''',
            ( 0, 0, 0, twitchChannel, userId )
        )

        connection.commit()
        cursor.close()

        return TriviaScoreResult(
            streak = 0,
            totalLosses = 0,
            totalWins = 0,
            twitchChannel = twitchChannel,
            userId = userId
        )

    def incrementTotalLosses(
        self,
        twitchChannel: str,
        userId: str
    ) -> TriviaScoreResult:
        if not utils.isValidStr(twitchChannel):
            raise ValueError(f'twitchChannel argument is malformed: \"{twitchChannel}\"')
        elif not utils.isValidStr(userId):
            raise ValueError(f'userId argument is malformed: \"{userId}\"')
        elif userId == '0':
            raise ValueError(f'userId argument is an illegal value: \"{userId}\"')

        result = self.fetchTriviaScore(
            twitchChannel = twitchChannel,
            userId = userId
        )

        newStreak: int = 0
        if result.getStreak() <= -1:
            newStreak = result.getStreak() - 1
        else:
            newStreak = -1

        newTotalLosses: int = result.getTotalLosses() + 1

        newResult = TriviaScoreResult(
            streak = newStreak,
            totalLosses = newTotalLosses,
            totalWins = result.getTotalWins(),
            twitchChannel = result.getTwitchChannel(),
            userId = result.getUserId()
        )

        self.__updateTriviaScore(
            newStreak = newResult.getStreak(),
            newTotalLosses = newResult.getTotalLosses(),
            newTotalWins = newResult.getTotalWins(),
            twitchChannel = newResult.getTwitchChannel(),
            userId = newResult.getUserId()
        )

        return newResult

    def incrementTotalWins(
        self,
        twitchChannel: str,
        userId: str
    ) -> TriviaScoreResult:
        if not utils.isValidStr(twitchChannel):
            raise ValueError(f'twitchChannel argument is malformed: \"{twitchChannel}\"')
        elif not utils.isValidStr(userId):
            raise ValueError(f'userId argument is malformed: \"{userId}\"')
        elif userId == '0':
            raise ValueError(f'userId argument is an illegal value: \"{userId}\"')

        result = self.fetchTriviaScore(
            twitchChannel = twitchChannel,
            userId = userId
        )

        newStreak: int = 0
        if result.getStreak() >= 1:
            newStreak = result.getStreak() + 1
        else:
            newStreak = 1

        newTotalWins: int = result.getTotalWins() + 1

        newResult = TriviaScoreResult(
            streak = newStreak,
            totalLosses = result.getTotalLosses(),
            totalWins = newTotalWins,
            twitchChannel = result.getTwitchChannel(),
            userId = result.getUserId()
        )

        self.__updateTriviaScore(
            newStreak = newResult.getStreak(),
            newTotalLosses = newResult.getTotalLosses(),
            newTotalWins = newResult.getTotalWins(),
            twitchChannel = newResult.getTwitchChannel(),
            userId = newResult.getUserId()
        )

        return newResult

    def __updateTriviaScore(
        self,
        newStreak: int,
        newTotalLosses: int,
        newTotalWins: int,
        twitchChannel: str,
        userId: str
    ):
        if not utils.isValidNum(newStreak):
            raise ValueError(f'newStreak argument is malformed: \"{newStreak}\"')
        elif not utils.isValidNum(newTotalLosses):
            raise ValueError(f'newTotalLosses argument is malformed: \"{newTotalLosses}\"')
        elif not utils.isValidNum(newTotalWins):
            raise ValueError(f'newTotalWins argument is malformed: \"{newTotalWins}\"')
        elif not utils.isValidStr(twitchChannel):
            raise ValueError(f'twitchChannel argument is malformed: \"{twitchChannel}\"')
        elif not utils.isValidStr(userId):
            raise ValueError(f'userId argument is malformed: \"{userId}\"')
        elif userId == '0':
            raise ValueError(f'userId argument is an illegal value: \"{userId}\"')

        connection = self.__backingDatabase.getConnection()
        cursor = connection.cursor()
        cursor.execute(
            '''
                INSERT INTO triviaScores (streak, totalLosses, totalWins, twitchChannel, userId)
                VALUES (?, ?, ?, ?, ?)
                ON CONFLICT (twitchChannel, userId) DO UPDATE SET streak = excluded.streak, totalLosses = excluded.totalLosses, totalWins = excluded.totalWins
            ''',
            ( newStreak, newTotalLosses, newTotalWins, twitchChannel, userId )
        )

        connection.commit()
        cursor.close()

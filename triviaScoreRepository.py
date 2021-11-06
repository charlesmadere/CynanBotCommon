import locale

try:
    import CynanBotCommon.utils as utils
    from CynanBotCommon.backingDatabase import BackingDatabase
except:
    import utils
    from backingDatabase import BackingDatabase


class TriviaScoreResult():

    def __init__(
        self,
        streak: int,
        totalLosses: int,
        totalWins: int,
        twitchChannel: str,
        userId: str
    ):
        if not utils.isValidNum(streak):
            raise ValueError(f'streak argument is malformed: \"{streak}\"')
        elif not utils.isValidNum(totalLosses):
            raise ValueError(f'totalLosses argument is malformed: \"{totalLosses}\"')
        elif not utils.isValidNum(totalWins):
            raise ValueError(f'totalWins argument is malformed: \"{totalWins}\"')
        elif not utils.isValidStr(twitchChannel):
            raise ValueError(f'twitchChannel argument is malformed: \"{twitchChannel}\"')
        elif not utils.isValidStr(userId):
            raise ValueError(f'userId argument is malformed: \"{userId}\"')

        self.__streak: int = streak
        self.__totalLosses: int = totalLosses
        self.__totalWins: int = totalWins
        self.__twitchChannel: str = twitchChannel
        self.__userId: str = userId

    def getStreak(self) -> int:
        return self.__streak

    def getStreakStr(self) -> str:
        return locale.format_string("%d", self.__streak, grouping = True)

    def getTotal(self) -> int:
        return self.__totalLosses + self.__totalWins

    def getTotalStr(self) -> str:
        return locale.format_string("%d", self.getTotal(), grouping = True)

    def getTotalLosses(self) -> int:
        return self.__totalLosses

    def getTotalLossesStr(self) -> str:
        return locale.format_string("%d", self.__totalLosses, grouping = True)

    def getTotalWins(self) -> int:
        return self.__totalWins

    def getTotalWinsStr(self) -> str:
        return locale.format_string("%d", self.__totalWins, grouping = True)

    def getTwitchChannel(self) -> str:
        return self.__twitchChannel

    def getUserId(self) -> str:
        return self.__userId


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

    def fetchScore(
        self,
        twitchChannel: str,
        userId: str
    ) -> TriviaScoreResult:
        if not utils.isValidStr(twitchChannel):
            raise ValueError(f'twitchChannel argument is malformed: \"{twitchChannel}\"')
        elif not utils.isValidStr(userId):
            raise ValueError(f'userId argument is malformed: \"{userId}\"')

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

        result = self.fetchScore(
            twitchChannel = twitchChannel,
            userId = userId
        )

        newStreak: int = 0
        if result.getStreak() <= 0:
            newStreak = result.getStreak() - 1
        else:
            newStreak = -1

        newTotalLosses: int = result.getTotalLosses() + 1

        newResult = TriviaScoreResult(
            streak = newStreak,
            totalLosses = newTotalLosses,
            totalWins = result.getTotalWins(),
            twitchChanel = result.getTwitchChannel(),
            userId = result.getUserId()
        )

        self.__updateScore(
            newStreak = newResult.getStreak(),
            newTotalLosses = newResult.getTotalLosses(),
            newTotalWins = result.getTotalWins(),
            twitchChannel = result.getTwitchChannel(),
            userId = result.getUserId()
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

        result = self.fetchScore(
            twitchChannel = twitchChannel,
            userId = userId
        )

        newStreak: int = 0
        if result.getStreak() >= 0:
            newStreak = result.getStreak() + 1
        else:
            newStreak = 1

        newTotalWins: int = result.getTotalWins() + 1

        newResult = TriviaScoreResult(
            streak = newStreak,
            totalLosses = result.getTotalLosses(),
            totalWins = newTotalWins,
            twitchChanel = result.getTwitchChannel(),
            userId = result.getUserId()
        )

        self.__updateScore(
            newStreak = newResult.getStreak(),
            newTotalLosses = newResult.getTotalLosses(),
            newTotalWins = result.getTotalWins(),
            twitchChannel = result.getTwitchChannel(),
            userId = result.getUserId()
        )

        return newResult

    def __updateScore(
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

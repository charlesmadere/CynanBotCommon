from aiosqlite import Connection

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
        self.__isDatabaseReady: bool = False

    async def fetchTriviaScore(
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

        connection = await self.__getDatabaseConnection()
        cursor = await connection.execute(
            '''
                SELECT streak, superTriviaWins, totalLosses, totalWins, twitchChannel, userId FROM triviaScores
                WHERE twitchChannel = ? AND userId = ?
            ''',
            ( twitchChannel, userId )
        )

        row = await cursor.fetchone()

        if row is not None:
            result = TriviaScoreResult(
                streak = row[0],
                superTriviaWins = row[1],
                totalLosses = row[2],
                totalWins = row[3],
                twitchChannel = row[4],
                userId = row[5]
            )

            await cursor.close()
            await connection.close()
            return result

        await cursor.execute(
            '''
                INSERT INTO triviaScores (streak, superTriviaWins, totalLosses, totalWins, twitchChannel, userId)
                VALUES (?, ?, ?, ?, ?, ?)
            ''',
            ( 0, 0, 0, 0, twitchChannel, userId )
        )

        await connection.commit()
        await cursor.close()
        await connection.close()

        return TriviaScoreResult(
            streak = 0,
            superTriviaWins = 0,
            totalLosses = 0,
            totalWins = 0,
            twitchChannel = twitchChannel,
            userId = userId
        )

    async def incrementSuperTriviaWins(
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

        result = await self.fetchTriviaScore(
            twitchChannel = twitchChannel,
            userId = userId
        )

        newSuperTriviaWins: int = result.getSuperTriviaWins() + 1

        newResult = TriviaScoreResult(
            streak = result.getStreak(),
            superTriviaWins = newSuperTriviaWins,
            totalLosses = result.getTotalLosses(),
            totalWins = result.getTotalWins(),
            twitchChannel = result.getTwitchChannel(),
            userId = result.getUserId()
        )

        await self.__updateTriviaScore(
            newStreak = newResult.getStreak(),
            newSuperTriviaWins = newResult.getSuperTriviaWins(),
            newTotalLosses = newResult.getTotalLosses(),
            newTotalWins = newResult.getTotalWins(),
            twitchChannel = newResult.getTwitchChannel(),
            userId = newResult.getUserId()
        )

        return newResult

    async def incrementTotalLosses(
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

        result = await self.fetchTriviaScore(
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
            superTriviaWins = result.getSuperTriviaWins(),
            totalLosses = newTotalLosses,
            totalWins = result.getTotalWins(),
            twitchChannel = result.getTwitchChannel(),
            userId = result.getUserId()
        )

        await self.__updateTriviaScore(
            newStreak = newResult.getStreak(),
            newSuperTriviaWins = newResult.getSuperTriviaWins(),
            newTotalLosses = newResult.getTotalLosses(),
            newTotalWins = newResult.getTotalWins(),
            twitchChannel = newResult.getTwitchChannel(),
            userId = newResult.getUserId()
        )

        return newResult

    async def incrementTotalWins(
        self,
        alsoIncrementSuperTriviaWins: bool,
        twitchChannel: str,
        userId: str
    ) -> TriviaScoreResult:
        if not utils.isValidBool(alsoIncrementSuperTriviaWins):
            raise ValueError(f'alsoIncrementSuperTriviaWins argument is malformed: \"{alsoIncrementSuperTriviaWins}\"')
        elif not utils.isValidStr(twitchChannel):
            raise ValueError(f'twitchChannel argument is malformed: \"{twitchChannel}\"')
        elif not utils.isValidStr(userId):
            raise ValueError(f'userId argument is malformed: \"{userId}\"')
        elif userId == '0':
            raise ValueError(f'userId argument is an illegal value: \"{userId}\"')

        result = await self.fetchTriviaScore(
            twitchChannel = twitchChannel,
            userId = userId
        )

        newStreak: int = 0
        if result.getStreak() >= 1:
            newStreak = result.getStreak() + 1
        else:
            newStreak = 1

        newSuperTriviaWins: int = result.getSuperTriviaWins()
        if alsoIncrementSuperTriviaWins:
            newSuperTriviaWins = newSuperTriviaWins + 1

        newTotalWins: int = result.getTotalWins() + 1

        newResult = TriviaScoreResult(
            streak = newStreak,
            superTriviaWins = newSuperTriviaWins,
            totalLosses = result.getTotalLosses(),
            totalWins = newTotalWins,
            twitchChannel = result.getTwitchChannel(),
            userId = result.getUserId()
        )

        await self.__updateTriviaScore(
            newStreak = newResult.getStreak(),
            newSuperTriviaWins = newResult.getSuperTriviaWins(),
            newTotalLosses = newResult.getTotalLosses(),
            newTotalWins = newResult.getTotalWins(),
            twitchChannel = newResult.getTwitchChannel(),
            userId = newResult.getUserId()
        )

        return newResult

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
                CREATE TABLE IF NOT EXISTS triviaScores (
                    streak INTEGER NOT NULL DEFAULT 0,
                    superTriviaWins INTEGER NOT NULL DEFAULT 0,
                    totalLosses INTEGER NOT NULL DEFAULT 0,
                    totalWins INTEGER NOT NULL DEFAULT 0,
                    twitchChannel TEXT NOT NULL COLLATE NOCASE,
                    userId TEXT NOT NULL COLLATE NOCASE,
                    PRIMARY KEY (twitchChannel, userId)
                )
            '''
        )

        await connection.commit()
        await cursor.close()
        await connection.close()

    async def __updateTriviaScore(
        self,
        newStreak: int,
        newSuperTriviaWins: int,
        newTotalLosses: int,
        newTotalWins: int,
        twitchChannel: str,
        userId: str
    ):
        if not utils.isValidNum(newStreak):
            raise ValueError(f'newStreak argument is malformed: \"{newStreak}\"')
        elif not utils.isValidNum(newSuperTriviaWins):
            raise ValueError(f'newSuperTriviaWins argument is malformed: \"{newSuperTriviaWins}\"')
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

        connection = await self.__backingDatabase.getConnection()
        cursor = await connection.execute(
            '''
                INSERT INTO triviaScores (streak, superTriviaWins, totalLosses, totalWins, twitchChannel, userId)
                VALUES (?, ?, ?, ?, ?, ?)
                ON CONFLICT (twitchChannel, userId) DO UPDATE SET streak = excluded.streak, superTriviaWins = excluded.superTriviaWins, totalLosses = excluded.totalLosses, totalWins = excluded.totalWins
            ''',
            ( newStreak, newSuperTriviaWins, newTotalLosses, newTotalWins, twitchChannel, userId )
        )

        await connection.commit()
        await cursor.close()
        await connection.close()

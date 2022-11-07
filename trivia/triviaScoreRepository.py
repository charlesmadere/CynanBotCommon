from asyncpg import Connection

try:
    import CynanBotCommon.utils as utils
    from CynanBotCommon.storage.backingPsqlDatabase import BackingPsqlDatabase
    from CynanBotCommon.trivia.triviaScoreResult import TriviaScoreResult
except:
    import utils
    from storage.backingPsqlDatabase import BackingPsqlDatabase
    from trivia.triviaScoreResult import TriviaScoreResult


class TriviaScoreRepository():

    def __init__(self, backingDatabase: BackingPsqlDatabase):
        if backingDatabase is None:
            raise ValueError(f'backingDatabase argument is malformed: \"{backingDatabase}\"')

        self.__backingDatabase: BackingPsqlDatabase = backingDatabase
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
        record = await connection.fetchrow(
            '''
                SELECT streak, superTriviaWins, triviaLosses, triviaWins, twitchChannel, userId FROM triviaScores
                WHERE twitchChannel = ? AND userId = ?
            ''',
            twitchChannel, userId
        )

        if record is not None:
            result = TriviaScoreResult(
                streak = record[0],
                superTriviaWins = record[1],
                triviaLosses = record[2],
                triviaWins = record[3],
                twitchChannel = record[4],
                userId = record[5]
            )

            await connection.close()
            return result

        async with connection.transaction():
            await connection.execute(
                '''
                    INSERT INTO triviaScores (streak, superTriviaWins, triviaLosses, triviaWins, twitchChannel, userId)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''',
                0, 0, 0, 0, twitchChannel, userId
            )

        await connection.close()
        return TriviaScoreResult(
            streak = 0,
            superTriviaWins = 0,
            triviaLosses = 0,
            triviaWins = 0,
            twitchChannel = twitchChannel,
            userId = userId
        )

    async def __getDatabaseConnection(self) -> Connection:
        await self.__initDatabaseTable()
        return await self.__backingDatabase.getConnection()

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
            triviaLosses = result.getTriviaLosses(),
            triviaWins = result.getTriviaWins(),
            twitchChannel = result.getTwitchChannel(),
            userId = result.getUserId()
        )

        await self.__updateTriviaScore(
            newStreak = newResult.getStreak(),
            newSuperTriviaWins = newResult.getSuperTriviaWins(),
            newTriviaLosses = newResult.getTriviaLosses(),
            newTriviaWins = newResult.getTriviaWins(),
            twitchChannel = newResult.getTwitchChannel(),
            userId = newResult.getUserId()
        )

        return newResult

    async def incrementTriviaLosses(
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

        newTriviaLosses: int = result.getTriviaLosses() + 1

        newResult = TriviaScoreResult(
            streak = newStreak,
            superTriviaWins = result.getSuperTriviaWins(),
            triviaLosses = newTriviaLosses,
            triviaWins = result.getTriviaWins(),
            twitchChannel = result.getTwitchChannel(),
            userId = result.getUserId()
        )

        await self.__updateTriviaScore(
            newStreak = newResult.getStreak(),
            newSuperTriviaWins = newResult.getSuperTriviaWins(),
            newTriviaLosses = newResult.getTriviaLosses(),
            newTriviaWins = newResult.getTriviaWins(),
            twitchChannel = newResult.getTwitchChannel(),
            userId = newResult.getUserId()
        )

        return newResult

    async def incrementTriviaWins(
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
        if result.getStreak() >= 1:
            newStreak = result.getStreak() + 1
        else:
            newStreak = 1

        newTriviaWins: int = result.getTriviaWins() + 1

        newResult = TriviaScoreResult(
            streak = newStreak,
            superTriviaWins = result.getSuperTriviaWins(),
            triviaLosses = result.getTriviaLosses(),
            triviaWins = newTriviaWins,
            twitchChannel = result.getTwitchChannel(),
            userId = result.getUserId()
        )

        await self.__updateTriviaScore(
            newStreak = newResult.getStreak(),
            newSuperTriviaWins = newResult.getSuperTriviaWins(),
            newTriviaLosses = newResult.getTriviaLosses(),
            newTriviaWins = newResult.getTriviaWins(),
            twitchChannel = newResult.getTwitchChannel(),
            userId = newResult.getUserId()
        )

        return newResult

    async def __initDatabaseTable(self):
        if self.__isDatabaseReady:
            return

        self.__isDatabaseReady = True

        connection = await self.__backingDatabase.getConnection()

        async with connection.transaction():
            await connection.execute(
                '''
                    CREATE TABLE IF NOT EXISTS triviaScores (
                        streak INTEGER NOT NULL DEFAULT 0,
                        superTriviaWins INTEGER NOT NULL DEFAULT 0,
                        triviaLosses INTEGER NOT NULL DEFAULT 0,
                        triviaWins INTEGER NOT NULL DEFAULT 0,
                        twitchChannel TEXT NOT NULL COLLATE NOCASE,
                        userId TEXT NOT NULL COLLATE NOCASE,
                        PRIMARY KEY (twitchChannel, userId)
                    )
                '''
            )

        await connection.close()

    async def __updateTriviaScore(
        self,
        newStreak: int,
        newSuperTriviaWins: int,
        newTriviaLosses: int,
        newTriviaWins: int,
        twitchChannel: str,
        userId: str
    ):
        if not utils.isValidNum(newStreak):
            raise ValueError(f'newStreak argument is malformed: \"{newStreak}\"')
        elif not utils.isValidNum(newSuperTriviaWins):
            raise ValueError(f'newSuperTriviaWins argument is malformed: \"{newSuperTriviaWins}\"')
        elif newSuperTriviaWins < 0:
            raise ValueError(f'newSuperTriviaWins argument is out of bounds: {newSuperTriviaWins}')
        elif not utils.isValidNum(newTriviaLosses):
            raise ValueError(f'newTriviaLosses argument is malformed: \"{newTriviaLosses}\"')
        elif newTriviaLosses < 0:
            raise ValueError(f'newTriviaLosses argument is out of bounds: {newTriviaLosses}')
        elif not utils.isValidNum(newTriviaWins):
            raise ValueError(f'newTriviaWins argument is malformed: \"{newTriviaWins}\"')
        elif newTriviaWins < 0:
            raise ValueError(f'newTriviaWins argument is out of bounds: {newTriviaWins}')
        elif not utils.isValidStr(twitchChannel):
            raise ValueError(f'twitchChannel argument is malformed: \"{twitchChannel}\"')
        elif not utils.isValidStr(userId):
            raise ValueError(f'userId argument is malformed: \"{userId}\"')
        elif userId == '0':
            raise ValueError(f'userId argument is an illegal value: \"{userId}\"')

        connection = await self.__backingDatabase.getConnection()

        async with connection.transaction():
            await connection.execute(
                '''
                    INSERT INTO triviaScores (streak, superTriviaWins, triviaLosses, triviaWins, twitchChannel, userId)
                    VALUES (?, ?, ?, ?, ?, ?)
                    ON CONFLICT (twitchChannel, userId) DO UPDATE SET streak = excluded.streak, superTriviaWins = excluded.superTriviaWins, triviaLosses = excluded.triviaLosses, triviaWins = excluded.triviaWins
                ''',
                newStreak, newSuperTriviaWins, newTriviaLosses, newTriviaWins, twitchChannel, userId
            )

        await connection.close()

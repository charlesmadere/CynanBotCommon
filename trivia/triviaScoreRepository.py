try:
    import CynanBotCommon.utils as utils
    from CynanBotCommon.storage.backingDatabase import BackingDatabase
    from CynanBotCommon.storage.databaseConnection import DatabaseConnection
    from CynanBotCommon.storage.databaseType import DatabaseType
    from CynanBotCommon.trivia.triviaScoreResult import TriviaScoreResult
except:
    import utils
    from storage.backingDatabase import BackingDatabase
    from storage.databaseConnection import DatabaseConnection
    from storage.databaseType import DatabaseType
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
        record = await connection.fetchRow(
            '''
                SELECT streak, supertriviawins, trivialosses, triviawins, twitchchannel, userid FROM triviascores
                WHERE twitchchannel = $1 AND userid = $2
                LIMIT 1
            ''',
            twitchChannel, userId
        )

        if utils.hasItems(record):
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

        await connection.execute(
            '''
                INSERT INTO triviascores (streak, supertriviawins, trivialosses, triviawins, twitchchannel, userid)
                VALUES ($1, $2, $3, $4, $5, $6)
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

    async def __getDatabaseConnection(self) -> DatabaseConnection:
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

        if connection.getDatabaseType() is DatabaseType.POSTGRESQL:
            await connection.createTableIfNotExists(
                '''
                    CREATE TABLE IF NOT EXISTS triviascores (
                        streak integer DEFAULT 0 NOT NULL,
                        supertriviawins integer DEFAULT 0 NOT NULL,
                        trivialosses integer DEFAULT 0 NOT NULL,
                        triviawins integer DEFAULT 0 NOT NULL,
                        twitchchannel public.citext NOT NULL,
                        userid public.citext NOT NULL,
                        PRIMARY KEY (twitchchannel, userid)
                    )
                '''
            )
        elif connection.getDatabaseType() is DatabaseType.SQLITE:
            await connection.createTableIfNotExists(
                '''
                    CREATE TABLE IF NOT EXISTS triviascores (
                        streak INTEGER NOT NULL DEFAULT 0,
                        supertriviawins INTEGER NOT NULL DEFAULT 0,
                        trivialosses INTEGER NOT NULL DEFAULT 0,
                        triviawins INTEGER NOT NULL DEFAULT 0,
                        twitchchannel TEXT NOT NULL COLLATE NOCASE,
                        userid TEXT NOT NULL COLLATE NOCASE,
                        PRIMARY KEY (twitchchannel, userid)
                    )
                '''
            )
        else:
            raise RuntimeError(f'Encountered unexpected DatabaseType when trying to create tables: \"{connection.getDatabaseType()}\"')

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
        await connection.execute(
            '''
                INSERT INTO triviascores (streak, supertriviawins, trivialosses, triviawins, twitchchannel, userid)
                VALUES ($1, $2, $3, $4, $5, $6)
                ON CONFLICT (twitchchannel, userid) DO UPDATE SET streak = EXCLUDED.streak, supertriviawins = EXCLUDED.supertriviawins, triviaLosses = EXCLUDED.trivialosses, triviawins = EXCLUDED.triviawins
            ''',
            newStreak, newSuperTriviaWins, newTriviaLosses, newTriviaWins, twitchChannel, userId
        )

        await connection.close()

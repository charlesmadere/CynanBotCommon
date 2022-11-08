from typing import List, Optional

try:
    import CynanBotCommon.utils as utils
    from CynanBotCommon.cuteness.cutenessChampionsResult import \
        CutenessChampionsResult
    from CynanBotCommon.cuteness.cutenessDate import CutenessDate
    from CynanBotCommon.cuteness.cutenessEntry import CutenessEntry
    from CynanBotCommon.cuteness.cutenessHistoryEntry import \
        CutenessHistoryEntry
    from CynanBotCommon.cuteness.cutenessHistoryResult import \
        CutenessHistoryResult
    from CynanBotCommon.cuteness.cutenessLeaderboardEntry import \
        CutenessLeaderboardEntry
    from CynanBotCommon.cuteness.cutenessLeaderboardHistoryResult import \
        CutenessLeaderboardHistoryResult
    from CynanBotCommon.cuteness.cutenessLeaderboardResult import \
        CutenessLeaderboardResult
    from CynanBotCommon.cuteness.cutenessResult import CutenessResult
    from CynanBotCommon.storage.backingDatabase import BackingDatabase
    from CynanBotCommon.storage.databaseConnection import DatabaseConnection
    from CynanBotCommon.users.userIdsRepository import UserIdsRepository
except:
    import utils
    from cuteness.cutenessChampionsResult import CutenessChampionsResult
    from cuteness.cutenessDate import CutenessDate
    from cuteness.cutenessEntry import CutenessEntry
    from cuteness.cutenessHistoryEntry import CutenessHistoryEntry
    from cuteness.cutenessHistoryResult import CutenessHistoryResult
    from cuteness.cutenessLeaderboardEntry import CutenessLeaderboardEntry
    from cuteness.cutenessLeaderboardHistoryResult import \
        CutenessLeaderboardHistoryResult
    from cuteness.cutenessLeaderboardResult import CutenessLeaderboardResult
    from cuteness.cutenessResult import CutenessResult
    from storage.backingDatabase import BackingDatabase
    from storage.databaseConnection import DatabaseConnection

    from users.userIdsRepository import UserIdsRepository


class CutenessRepository():

    def __init__(
        self,
        backingDatabase: BackingDatabase,
        userIdsRepository: UserIdsRepository,
        historyLeaderboardSize: int = 3,
        historySize: int = 5,
        leaderboardSize: int = 10,
        localLeaderboardSize: int = 5
    ):
        if backingDatabase is None:
            raise ValueError(f'backingDatabase argument is malformed: \"{backingDatabase}\"')
        elif userIdsRepository is None:
            raise ValueError(f'userIdsRepository argument is malformed: \"{userIdsRepository}\"')
        elif not utils.isValidNum(historyLeaderboardSize):
            raise ValueError(f'historyLeaderboardSize argument is malformed: \"{historyLeaderboardSize}\"')
        elif historyLeaderboardSize < 2 or historyLeaderboardSize > 6:
            raise ValueError(f'historyLeaderboardSize argument is out of bounds: {historyLeaderboardSize}')
        elif not utils.isValidNum(historySize):
            raise ValueError(f'historySize argument is malformed: \"{historySize}\"')
        elif historySize < 2 or historySize > 12:
            raise ValueError(f'historySize argument is out of bounds: {historySize}')
        elif not utils.isValidNum(leaderboardSize):
            raise ValueError(f'leaderboardSize argument is malformed: \"{leaderboardSize}\"')
        elif leaderboardSize < 3 or leaderboardSize > 10:
            raise ValueError(f'leaderboardSize argument is out of bounds: {leaderboardSize}')
        elif not utils.isValidNum(localLeaderboardSize):
            raise ValueError(f'localLeaderboardSize argument is malformed: \"{localLeaderboardSize}\"')
        elif localLeaderboardSize < 1 or localLeaderboardSize > 5:
            raise ValueError(f'localLeaderboardSize argument is out of bounds: {localLeaderboardSize}')

        self.__backingDatabase: BackingDatabase = backingDatabase
        self.__userIdsRepository: UserIdsRepository = userIdsRepository
        self.__historyLeaderboardSize: int = historyLeaderboardSize
        self.__historySize: int = historySize
        self.__leaderboardSize: int = leaderboardSize
        self.__localLeaderboardSize: int = localLeaderboardSize

        self.__isDatabaseReady: bool = False

    async def fetchCuteness(
        self,
        fetchLocalLeaderboard: bool,
        twitchChannel: str,
        userId: str,
        userName: str,
    ) -> CutenessResult:
        if not utils.isValidBool(fetchLocalLeaderboard):
            raise ValueError(f'fetchLocalLeaderboard argument is malformed: \"{fetchLocalLeaderboard}\"')
        elif not utils.isValidStr(twitchChannel):
            raise ValueError(f'twitchChannel argument is malformed: \"{twitchChannel}\"')
        elif not utils.isValidStr(userId):
            raise ValueError(f'userId argument is malformed: \"{userId}\"')
        elif userId == '0':
            raise ValueError(f'userId argument is an illegal value: \"{userId}\"')
        elif not utils.isValidStr(userName):
            raise ValueError(f'userName argument is malformed: \"{userName}\"')

        await self.__userIdsRepository.setUser(userId = userId, userName = userName)

        cutenessDate = CutenessDate()

        connection = await self.__getDatabaseConnection()
        record = await connection.fetchrow(
            '''
                SELECT cuteness.cuteness, cuteness.userId, userIds.userName FROM cuteness
                INNER JOIN userIds ON cuteness.userId = userIds.userId
                WHERE cuteness.twitchChannel = ? AND cuteness.userId = ? AND cuteness.utcYearAndMonth = ?
                LIMIT 1
            ''',
            twitchChannel, userId, cutenessDate.getStr()
        )

        if not utils.hasItems(record):
            await connection.close()
            return CutenessResult(
                cutenessDate = cutenessDate,
                cuteness = 0,
                localLeaderboard = None,
                userId = userId,
                userName = userName
            )

        cuteness: int = record[0]

        if not fetchLocalLeaderboard:
            await connection.close()
            return CutenessResult(
                cutenessDate = cutenessDate,
                cuteness = cuteness,
                localLeaderboard = None,
                userId = userId,
                userName = userName
            )

        twitchChannelUserId = await self.__userIdsRepository.fetchUserId(userName = twitchChannel)

        records = await connection.fetch(
            '''
                SELECT cuteness.cuteness, cuteness.userId, userIds.userName FROM cuteness
                INNER JOIN userIds ON cuteness.userId = userIds.userId
                WHERE cuteness.twitchChannel = ? AND cuteness.utcYearAndMonth = ? AND cuteness.cuteness IS NOT NULL AND cuteness.cuteness >= 1 AND cuteness.userId != ? AND cuteness.userId != ?
                ORDER BY ABS(? - ABS(cuteness.cuteness)) ASC
                LIMIT ?
            ''',
            twitchChannel, cutenessDate.getStr(), userId, twitchChannelUserId, cuteness, self.__localLeaderboardSize
        )

        if not utils.hasItems(records):
            await connection.close()
            return CutenessResult(
                cutenessDate = cutenessDate,
                cuteness = cuteness,
                localLeaderboard = None,
                userId = userId,
                userName = userName
            )

        localLeaderboard: List[CutenessEntry] = list()

        for record in records:
            localLeaderboard.append(CutenessEntry(
                cuteness = record[0],
                userId = record[1],
                userName = record[2]
            ))

        await connection.close()

        # sorts cuteness into highest to lowest order
        localLeaderboard.sort(key = lambda entry: entry.getCuteness(), reverse = True)

        return CutenessResult(
            cutenessDate = cutenessDate,
            cuteness = cuteness,
            localLeaderboard = localLeaderboard,
            userId = userId,
            userName = userName
        )

    async def fetchCutenessChampions(self, twitchChannel: str) -> CutenessChampionsResult:
        if not utils.isValidStr(twitchChannel):
            raise ValueError(f'twitchChannel argument is malformed: \"{twitchChannel}\"')

        twitchChannelUserId = await self.__userIdsRepository.fetchUserId(userName = twitchChannel)

        connection = await self.__getDatabaseConnection()
        records = await connection.fetch(
            '''
                SELECT cuteness.userId, userIds.userName, SUM(cuteness.cuteness) as totalCuteness FROM cuteness
                INNER JOIN userIds on cuteness.userId = userIds.userId where cuteness.twitchChannel = ? AND cuteness.userId != ?
                GROUP BY cuteness.userId
                ORDER BY SUM(cuteness.cuteness) DESC
                LIMIT ?
            ''',
            twitchChannel, twitchChannelUserId, self.__leaderboardSize
        )

        if not utils.hasItems(records):
            await connection.close()
            return CutenessChampionsResult(twitchChannel = twitchChannel)

        champions: List[CutenessLeaderboardEntry] = list()
        rank: int = 1

        for record in records:
            champions.append(CutenessLeaderboardEntry(
                cuteness = record[2],
                rank = rank,
                userId = record[0],
                userName = record[1]
            ))
            rank = rank + 1

        await connection.close()

        # sort cuteness into highest to lowest order
        champions.sort(key = lambda champion: champion.getCuteness(), reverse = True)

        return CutenessChampionsResult(
            twitchChannel = twitchChannel,
            champions = champions
        )

    async def fetchCutenessHistory(
        self,
        twitchChannel: str,
        userId: str,
        userName: str
    ) -> CutenessHistoryResult:
        if not utils.isValidStr(twitchChannel):
            raise ValueError(f'twitchChannel argument is malformed: \"{twitchChannel}\"')
        elif not utils.isValidStr(userId):
            raise ValueError(f'userId argument is malformed: \"{userId}\"')
        elif userId == '0':
            raise ValueError(f'userId argument is an illegal value: \"{userId}\"')
        elif not utils.isValidStr(userName):
            raise ValueError(f'userName argument is malformed: \"{userName}\"')

        await self.__userIdsRepository.setUser(userId = userId, userName = userName)

        connection = await self.__getDatabaseConnection()
        records = await connection.fetchRow(
            '''
                SELECT cuteness, utcYearAndMonth FROM cuteness
                WHERE twitchChannel = ? AND userId = ? AND cuteness IS NOT NULL AND cuteness >= 1
                ORDER BY utcYearAndMonth DESC
                LIMIT ?
            ''',
            twitchChannel, userId, self.__historySize
        )

        if not utils.hasItems(records):
            await connection.close()
            return CutenessHistoryResult(
                userId = userId,
                userName = userName
            )

        entries: List[CutenessHistoryEntry] = list()

        for record in records:
            entries.append(CutenessHistoryEntry(
                cutenessDate = CutenessDate(record[1]),
                cuteness = record[0],
                userId = userId,
                userName = userName
            ))

        # sort entries into newest to oldest order
        entries.sort(key = lambda entry: entry.getCutenessDate(), reverse = True)

        record = await connection.fetchRow(
            '''
                SELECT SUM(cuteness) FROM cuteness
                WHERE twitchChannel = ? AND userId = ? AND cuteness IS NOT NULL AND cuteness >= 1
                LIMIT 1
            ''',
            twitchChannel, userId
        )

        totalCuteness: int = 0

        if utils.hasItems(record):
            # this should be impossible at this point, but let's just be safe
            totalCuteness = record[0]

        record = await connection.fetchRow(
            '''
                SELECT cuteness, utcYearAndMonth FROM cuteness
                WHERE twitchChannel = ? AND userId = ? AND cuteness IS NOT NULL AND cuteness >= 1
                ORDER BY cuteness DESC
                LIMIT 1
            ''',
            twitchChannel, userId
        )

        bestCuteness: CutenessHistoryEntry = None

        if utils.hasItems(record):
            # again, this should be impossible here, but let's just be safe
            bestCuteness = CutenessHistoryEntry(
                cutenessDate = CutenessDate(record[1]),
                cuteness = record[0],
                userId = userId,
                userName = userName
            )

        await connection.close()
        return CutenessHistoryResult(
            userId = userId,
            userName = userName,
            bestCuteness = bestCuteness,
            totalCuteness = totalCuteness,
            entries = entries
        )

    async def fetchCutenessIncrementedBy(
        self,
        incrementAmount: int,
        twitchChannel: str,
        userId: str,
        userName: str
    ) -> CutenessResult:
        if not utils.isValidNum(incrementAmount):
            raise ValueError(f'incrementAmount argument is malformed: \"{incrementAmount}\"')
        elif incrementAmount >= utils.getLongMaxSafeSize():
            raise ValueError(f'incrementAmount ({incrementAmount}) is >= maximum value ({utils.getLongMaxSafeSize()})')
        elif incrementAmount <= utils.getLongMinSafeSize():
            raise ValueError(f'incrementAmount ({incrementAmount}) is <= minimum value ({utils.getLongMinSafeSize()})')
        elif not utils.isValidStr(twitchChannel):
            raise ValueError(f'twitchChannel argument is malformed: \"{twitchChannel}\"')
        elif not utils.isValidStr(userId):
            raise ValueError(f'userId argument is malformed: \"{userId}\"')
        elif userId == '0':
            raise ValueError(f'userId argument is an illegal value: \"{userId}\"')
        elif not utils.isValidStr(userName):
            raise ValueError(f'userName argument is malformed: \"{userName}\"')

        await self.__userIdsRepository.setUser(userId = userId, userName = userName)

        cutenessDate = CutenessDate()

        connection = await self.__getDatabaseConnection()
        record = await connection.fetchRow(
            '''
                SELECT cuteness FROM cuteness
                WHERE twitchChannel = ? AND userId = ? AND utcYearAndMonth = ?
                LIMIT 1
            ''',
            twitchChannel, userId, cutenessDate.getStr()
        )

        oldCuteness: int = 0

        if utils.hasItems(record):
            oldCuteness = record[0]

        newCuteness: int = oldCuteness + incrementAmount

        if newCuteness < 0:
            newCuteness = 0
        elif newCuteness > utils.getLongMaxSafeSize():
            raise OverflowError(f'New cuteness ({newCuteness}) would be too large (old cuteness = {oldCuteness}) (increment amount = {incrementAmount})')

        await connection.execute(
            '''
                INSERT INTO cuteness (cuteness, twitchChannel, userId, utcYearAndMonth)
                VALUES (?, ?, ?, ?)
                ON CONFLICT (twitchChannel, userId, utcYearAndMonth) DO UPDATE SET cuteness = EXCLUDED.cuteness
            ''',
            newCuteness, twitchChannel, userId, cutenessDate.getStr()
        )

        await connection.close()

        return CutenessResult(
            cutenessDate = cutenessDate,
            cuteness = newCuteness,
            localLeaderboard = None,
            userId = userId,
            userName = userName
        )

    async def fetchCutenessLeaderboard(
        self,
        twitchChannel: str,
        specificLookupUserId: Optional[str] = None,
        specificLookupUserName: Optional[str] = None
    ) -> CutenessLeaderboardResult:
        if not utils.isValidStr(twitchChannel):
            raise ValueError(f'twitchChannel argument is malformed: \"{twitchChannel}\"')

        twitchChannelUserId = await self.__userIdsRepository.fetchUserId(userName = twitchChannel)

        cutenessDate = CutenessDate()
        connection = await self.__getDatabaseConnection()
        records = await connection.fetchRows(
            '''
                SELECT cuteness.cuteness, cuteness.userId, userIds.userName FROM cuteness
                INNER JOIN userIds ON cuteness.userId = userIds.userId
                WHERE cuteness.twitchChannel = ? AND cuteness.utcYearAndMonth = ? AND cuteness.cuteness IS NOT NULL AND cuteness.cuteness >= 1 AND cuteness.userId != ?
                ORDER BY cuteness.cuteness DESC
                LIMIT ?
            ''',
            twitchChannel, cutenessDate.getStr(), twitchChannelUserId, self.__leaderboardSize
        )

        if not utils.hasItems(records):
            await connection.close()
            return CutenessLeaderboardResult(cutenessDate = cutenessDate)

        entries: List[CutenessLeaderboardEntry] = list()
        rank: int = 1

        for record in records:
            entries.append(CutenessLeaderboardEntry(
                cuteness = record[0],
                rank = rank,
                userId = record[1],
                userName = record[2]
            ))
            rank = rank + 1

        await connection.close()

        # sort cuteness into highest to lowest order
        entries.sort(key = lambda entry: entry.getCuteness(), reverse = True)

        specificLookupAlreadyInResults: bool = False
        if utils.isValidStr(specificLookupUserId) or utils.isValidStr(specificLookupUserName):
            for entry in entries:
                if utils.isValidStr(specificLookupUserId) and entry.getUserId().lower() == specificLookupUserId.lower():
                    specificLookupAlreadyInResults = True
                    break
                elif utils.isValidStr(specificLookupUserName) and entry.getUserName().lower() == specificLookupUserName.lower():
                    specificLookupAlreadyInResults = True
                    break

        specificLookupCutenessResult: CutenessResult = None
        if not specificLookupAlreadyInResults and (utils.isValidStr(specificLookupUserId) or utils.isValidStr(specificLookupUserName)):
            if not utils.isValidStr(specificLookupUserId):
                try:
                    specificLookupUserId = await self.__userIdsRepository.fetchUserId(userName = specificLookupUserName)
                except ValueError:
                    # this exception can be safely ignored
                    pass
            else:
                try:
                    specificLookupUserName = await self.__userIdsRepository.fetchUserName(specificLookupUserId)
                except (RuntimeError, ValueError):
                    # this exception can be safely ignored
                    pass

            if utils.isValidStr(specificLookupUserId) and utils.isValidStr(specificLookupUserName):
                specificLookupCutenessResult = await self.fetchCuteness(
                    fetchLocalLeaderboard = False,
                    twitchChannel = twitchChannel,
                    userId = specificLookupUserId,
                    userName = specificLookupUserName
                )

        return CutenessLeaderboardResult(
            cutenessDate = cutenessDate,
            entries = entries,
            specificLookupCutenessResult = specificLookupCutenessResult
        )

    async def fetchCutenessLeaderboardHistory(self, twitchChannel: str) -> CutenessLeaderboardHistoryResult:
        if not utils.isValidStr(twitchChannel):
            raise ValueError(f'twitchChannel argument is malformed: \"{twitchChannel}\"')

        twitchChannelUserId = await self.__userIdsRepository.fetchUserId(userName = twitchChannel)

        connection = await self.__getDatabaseConnection()
        records = await connection.fetchRows(
            '''
                SELECT DISTINCT utcYearAndMonth FROM cuteness
                WHERE twitchChannel = ? AND utcYearAndMonth != ?
                ORDER BY utcYearAndMonth DESC
                LIMIT ?
            ''',
            twitchChannel, CutenessDate().getStr(), self.__historyLeaderboardSize
        )

        if not utils.hasItems(records):
            await connection.close()
            return CutenessLeaderboardHistoryResult(twitchChannel = twitchChannel)

        leaderboards: List[CutenessLeaderboardResult] = list()

        for record in records:
            cutenessDate = CutenessDate(record[0])
            monthRecords = await connection.fetchRows(
                '''
                    SELECT cuteness.cuteness, cuteness.userId, userIds.userName FROM cuteness
                    INNER JOIN userIds ON cuteness.userId = userIds.userId
                    WHERE cuteness.cuteness IS NOT NULL AND cuteness.cuteness >= 1 AND cuteness.twitchChannel = ? AND cuteness.userId != ? AND cuteness.utcYearAndMonth = ?
                    ORDER BY cuteness.cuteness DESC
                    LIMIT ?
                ''',
                twitchChannel, twitchChannelUserId, cutenessDate.getStr(), self.__historyLeaderboardSize
            )

            if not utils.hasItems(monthRecords):
                continue

            entries: List[CutenessLeaderboardEntry] = list()
            rank: int = 1

            for monthRecord in monthRecords:
                entries.append(CutenessLeaderboardEntry(
                    cuteness = monthRecord[0],
                    rank = rank,
                    userId = monthRecord[1],
                    userName = monthRecord[2]
                ))
                rank = rank + 1

            leaderboards.append(CutenessLeaderboardResult(
                cutenessDate = cutenessDate,
                entries = entries
            ))

        await connection.close()

        return CutenessLeaderboardHistoryResult(
            twitchChannel = twitchChannel,
            leaderboards = leaderboards
        )

    async def __getDatabaseConnection(self) -> DatabaseConnection:
        await self.__initDatabaseTable()
        return await self.__backingDatabase.getConnection()

    async def __initDatabaseTable(self):
        if self.__isDatabaseReady:
            return

        self.__isDatabaseReady = True

        connection = await self.__backingDatabase.getConnection()
        await connection.execute(
            '''
                CREATE TABLE IF NOT EXISTS cuteness (
                    cuteness BIGINT NOT NULL DEFAULT 0,
                    twitchChannel TEXT NOT NULL COLLATE NOCASE,
                    userId TEXT NOT NULL COLLATE NOCASE,
                    utcYearAndMonth TEXT NOT NULL COLLATE NOCASE,
                    PRIMARY KEY (twitchChannel, userId, utcYearAndMonth)
                )
            '''
        )

        await connection.close()

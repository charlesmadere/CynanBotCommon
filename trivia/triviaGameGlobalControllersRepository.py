from typing import List, Optional

try:
    import CynanBotCommon.utils as utils
    from CynanBotCommon.administratorProviderInterface import \
        AdministratorProviderInterface
    from CynanBotCommon.storage.backingDatabase import BackingDatabase
    from CynanBotCommon.storage.databaseConnection import DatabaseConnection
    from CynanBotCommon.storage.databaseType import DatabaseType
    from CynanBotCommon.timber.timber import Timber
    from CynanBotCommon.trivia.addTriviaGameControllerResult import \
        AddTriviaGameControllerResult
    from CynanBotCommon.trivia.removeTriviaGameControllerResult import \
        RemoveTriviaGameControllerResult
    from CynanBotCommon.trivia.triviaGameGlobalController import \
        TriviaGameGlobalController
    from CynanBotCommon.twitch.twitchTokensRepository import \
        TwitchTokensRepository
    from CynanBotCommon.users.userIdsRepository import UserIdsRepository
except:
    import utils
    from administratorProviderInterface import AdministratorProviderInterface
    from storage.backingDatabase import BackingDatabase
    from storage.databaseConnection import DatabaseConnection
    from storage.databaseType import DatabaseType
    from timber.timber import Timber
    from trivia.addTriviaGameControllerResult import \
        AddTriviaGameControllerResult
    from trivia.removeTriviaGameControllerResult import \
        RemoveTriviaGameControllerResult
    from trivia.triviaGameGlobalController import TriviaGameGlobalController

    from twitch.twitchTokensRepository import TwitchTokensRepository
    from users.userIdsRepository import UserIdsRepository


class TriviaGameGlobalControllersRepository():

    def __init__(
        self,
        administratorProviderInterface: AdministratorProviderInterface,
        backingDatabase: BackingDatabase,
        timber: Timber,
        twitchTokensRepository: TwitchTokensRepository,
        userIdsRepository: UserIdsRepository
    ):
        if not isinstance(administratorProviderInterface, AdministratorProviderInterface):
            raise ValueError(f'administratorProviderInterface argument is malformed: \"{administratorProviderInterface}\"')
        elif not isinstance(backingDatabase, BackingDatabase):
            raise ValueError(f'backingDatabase argument is malformed: \"{backingDatabase}\"')
        elif not isinstance(timber, Timber):
            raise ValueError(f'timber argument is malformed: \"{timber}\"')
        elif not isinstance(twitchTokensRepository, TwitchTokensRepository):
            raise ValueError(f'twitchTokensRepository argument is malformed: \"{twitchTokensRepository}\"')
        elif not isinstance(userIdsRepository, UserIdsRepository):
            raise ValueError(f'userIdsRepository argument is malformed: \"{userIdsRepository}\"')

        self.__administratorProviderInterface: AdministratorProviderInterface = administratorProviderInterface
        self.__backingDatabase: BackingDatabase = backingDatabase
        self.__timber: Timber = timber
        self.__twitchTokensRepository: TwitchTokensRepository = twitchTokensRepository
        self.__userIdsRepository: UserIdsRepository = userIdsRepository

        self.__isDatabaseReady: bool = False

    async def addController(self, userName: str) -> AddTriviaGameControllerResult:
        if not utils.isValidStr(userName):
            raise ValueError(f'userName argument is malformed: \"{userName}\"')

        administrator = await self.__administratorProviderInterface.getAdministrator()
        twitchAccessToken = await self.__twitchTokensRepository.getAccessToken(administrator)
        userId: Optional[str] = None

        try:
            userId = await self.__userIdsRepository.fetchUserId(
                userName = userName,
                twitchAccessToken = twitchAccessToken
            )
        except (RuntimeError, ValueError) as e:
            self.__timber.log('TriviaGameGlobalControllersRepository', f'Encountered exception when trying to add \"{userName}\" as a trivia game global controller: {e}', e)
            return AddTriviaGameControllerResult.ERROR

        if not utils.isValidStr(userId):
            self.__timber.log('TriviaGameGlobalControllersRepository', f'Retrieved no userId from UserIdsRepository when trying to add \"{userName}\" as a trivia game global controller: \"{userId}\"')
            return AddTriviaGameControllerResult.ERROR

        connection = await self.__getDatabaseConnection()
        record = await connection.fetchRow(
            '''
                SELECT COUNT(1) FROM triviagameglobalcontrollers
                WHERE userid = $1
                LIMIT 1
            ''',
            userId
        )

        count: Optional[int] = None
        if utils.hasItems(record):
            count = record[0]

        if utils.isValidInt(count) and count >= 1:
            await connection.close()
            self.__timber.log('TriviaGameGlobalControllersRepository', f'Tried to add userName=\"{userName}\" userId=\"{userId}\" as a trivia game global controller, but this user has already been added as one')
            return AddTriviaGameControllerResult.ALREADY_EXISTS

        await connection.execute(
            '''
                INSERT INTO triviagameglobalcontrollers (userid)
                VALUES ($1)
                ON CONFLICT (userid) DO NOTHING
            ''',
            userId
        )

        await connection.close()
        self.__timber.log('TriviaGameGlobalControllersRepository', f'Added userName=\"{userName}\" userId=\"{userId}\" as a trivia game global controller')

        return AddTriviaGameControllerResult.ADDED

    async def getControllers(self) -> List[TriviaGameGlobalController]:
        connection = await self.__getDatabaseConnection()
        records = await connection.fetchRows(
            '''
                SELECT triviagameglobalcontrollers.userid, userids.username FROM triviagameglobalcontrollers
                INNER JOIN userids ON triviagameglobalcontrollers.userid = userids.userid
                ORDER BY userids.username ASC
            '''
        )

        controllers: List[TriviaGameGlobalController] = list()

        if not utils.hasItems(records):
            await connection.close()
            return controllers

        for record in records:
            controllers.append(TriviaGameGlobalController(
                userId = record[0],
                userName = record[1]
            ))

        await connection.close()
        controllers.sort(key = lambda controller: controller.getUserName().lower())

        return controllers

    async def __getDatabaseConnection(self) -> DatabaseConnection:
        await self.__initDatabaseTable()
        return await self.__backingDatabase.getConnection()

    async def __initDatabaseTable(self):
        if self.__isDatabaseReady:
            return

        self.__isDatabaseReady = True
        connection = await self.__backingDatabase.getConnection()

        if connection.getDatabaseType() is DatabaseType.POSTGRESQL:
            await connection.createTableIfNotExists(
                '''
                    CREATE TABLE IF NOT EXISTS triviagameglobalcontrollers (
                        userid public.citext NOT NULL PRIMARY KEY
                    )
                '''
            )
        elif connection.getDatabaseType() is DatabaseType.SQLITE:
            await connection.createTableIfNotExists(
                '''
                    CREATE TABLE IF NOT EXISTS triviagameglobalcontrollers (
                        userid TEXT NOT NULL PRIMARY KEY COLLATE NOCASE
                    )
                '''
            )
        else:
            raise RuntimeError(f'Encountered unexpected DatabaseType when trying to create tables: \"{connection.getDatabaseType()}\"')

        await connection.close()

    async def removeController(self, userName: str) -> RemoveTriviaGameControllerResult:
        if not utils.isValidStr(userName):
            raise ValueError(f'userName argument is malformed: \"{userName}\"')

        userId: Optional[str] = None

        try:
            userId = await self.__userIdsRepository.fetchUserId(userName)
        except (RuntimeError, ValueError) as e:
            self.__timber.log('TriviaGameGlobalControllersRepository', f'Encountered exception when trying to remove \"{userName}\" as a trivia game global controller: {e}', e)
            return RemoveTriviaGameControllerResult.ERROR

        if not utils.isValidStr(userId):
            self.__timber.log('TriviaGameGlobalControllersRepository', f'Retrieved no userId from UserIdsRepository when trying to remove \"{userName}\" as a trivia game global controller')
            return RemoveTriviaGameControllerResult.ERROR

        connection = await self.__backingDatabase.getConnection()
        await connection.execute(
            '''
                DELETE FROM triviagameglobalcontrollers
                WHERE userid = $1
            ''',
            userId
        )

        await connection.close()
        self.__timber.log('TriviaGameGlobalControllersRepository', f'Removed userName=\"{userName}\" userId=\"{userId}\" as a trivia game global controller')

        return RemoveTriviaGameControllerResult.REMOVED

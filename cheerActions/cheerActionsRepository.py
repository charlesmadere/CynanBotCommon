from typing import Dict, List, Optional

try:
    import CynanBotCommon.utils as utils
    from CynanBotCommon.cheerActions.cheerAction import CheerAction
    from CynanBotCommon.cheerActions.cheerActionIdGeneratorInterface import \
        CheerActionIdGeneratorInterface
    from CynanBotCommon.cheerActions.cheerActionRequirement import \
        CheerActionRequirement
    from CynanBotCommon.cheerActions.cheerActionsRepositoryInterface import \
        CheerActionsRepositoryInterface
    from CynanBotCommon.cheerActions.cheerActionType import CheerActionType
    from CynanBotCommon.cheerActions.exceptions import (
        CheerActionAlreadyExistsException, TooManyCheerActionsException)
    from CynanBotCommon.storage.backingDatabase import BackingDatabase
    from CynanBotCommon.storage.databaseConnection import DatabaseConnection
    from CynanBotCommon.storage.databaseType import DatabaseType
    from CynanBotCommon.timber.timberInterface import TimberInterface
except:
    import utils
    from cheerActions.cheerAction import CheerAction
    from cheerActions.cheerActionIdGeneratorInterface import \
        CheerActionIdGeneratorInterface
    from cheerActions.cheerActionRequirement import CheerActionRequirement
    from cheerActions.cheerActionsRepositoryInterface import \
        CheerActionsRepositoryInterface
    from cheerActions.cheerActionType import CheerActionType
    from cheerActions.exceptions import (CheerActionAlreadyExistsException,
                                         TooManyCheerActionsException)
    from storage.backingDatabase import BackingDatabase
    from storage.databaseConnection import DatabaseConnection
    from storage.databaseType import DatabaseType
    from timber.timberInterface import TimberInterface


class CheerActionsRepository(CheerActionsRepositoryInterface):

    def __init__(
        self,
        backingDatabase: BackingDatabase,
        cheerActionIdGenerator: CheerActionIdGeneratorInterface,
        timber: TimberInterface,
        maximumPerUser: int = 8
    ):
        if not isinstance(backingDatabase, BackingDatabase):
            raise ValueError(f'backingDatabase argument is malformed: \"{backingDatabase}\"')
        elif not isinstance(cheerActionIdGenerator, CheerActionIdGeneratorInterface):
            raise ValueError(f'cheerActionIdGenerator argument is malformed: \"{cheerActionIdGenerator}\"')
        elif not isinstance(timber, TimberInterface):
            raise ValueError(f'timber argument is malformed: \"{timber}\"')
        elif not utils.isValidInt(maximumPerUser):
            raise ValueError(f'maximumPerUser argument is malformed: \"{maximumPerUser}\"')
        elif maximumPerUser < 1 or maximumPerUser > 12:
            raise ValueError(f'maximumPerUser argument is out of bounds: {maximumPerUser}')

        self.__backingDatabase: BackingDatabase = backingDatabase
        self.__cheerActionIdGenerator: CheerActionIdGeneratorInterface = cheerActionIdGenerator
        self.__timber: TimberInterface = timber
        self.__maximumPerUser: int = maximumPerUser

        self.__isDatabaseReady: bool = False
        self.__cache: Dict[str, Optional[List[CheerAction]]] = dict()

    async def addAction(self, action: CheerAction):
        if not isinstance(action, CheerAction):
            raise ValueError(f'action argument is malformed: \"{action}\"')

        actions = await self.getActions(action.getUserId())

        if action in actions:
            raise CheerActionAlreadyExistsException(f'Attempted to add {action=} but it already exists for this user ({actions=})')
        elif len(actions) + 1 > self.__maximumPerUser:
            raise TooManyCheerActionsException(f'Attempted to add {action=} but this user already has the maximum number of cheer actions (actions len: {len(actions)}) ({self.__maximumPerUser=})')

        actionId: Optional[str] = None
        action: Optional[CheerAction] = None

        while actionId is None or action is None:
            actionId = await self.__cheerActionIdGenerator.generateActionId()
            action = await self.getAction(actionId)

        connection = await self.__getDatabaseConnection()
        await connection.execute(
            '''
                INSERT INTO cheeractions (actionid, actionrequirement, actiontype, amount, durationseconds, userid)
                VALUES ($1, $2, $3, $4, $5, $6)
            ''',
            actionId, action.getActionRequirement().toStr(), action.getActionType().toStr(), action.getAmount(), action.getDurationSeconds(), action.getUserId()
        )

        await connection.close()
        self.__cache.pop(action.getUserId(), None)
        self.__timber.log('CheerActionsRepository', f'Added new cheer action ({action=})')

    async def clearCaches(self):
        self.__cache.clear()
        self.__timber.log('CheerActionsRepository', 'Caches cleared')

    async def deleteAction(self, actionId: str) -> Optional[CheerAction]:
        if not utils.isValidStr(actionId):
            raise ValueError(f'actionId argument is malformed: \"{actionId}\"')

        action = await self.getAction(actionId)

        if action is None:
            self.__timber.log('CheerActionsRepository', f'Attempted to delete cheer action ID \"{actionId}\", but it does not exist in the database')
            return None

        connection = await self.__getDatabaseConnection()
        await connection.execute(
            '''
                DELETE FROM cheeractions
                WHERE actionid = $1
            ''',
            actionId
        )

        await connection.close()
        self.__cache.pop(action.getUserId(), None)
        self.__timber.log('CheerActionsRepository', f'Deleted cheer action ({actionId=}) ({action=})')

        return action

    async def getAction(self, actionId: str) -> Optional[CheerAction]:
        if not utils.isValidStr(actionId):
            raise ValueError(f'actionId argument is malformed: \"{actionId}\"')

        connection = await self.__getDatabaseConnection()
        record = await connection.fetchRow(
            '''
                SELECT cheeractions.actionrequirement, cheeractions.actiontype, cheeractions.amount, cheeractions.durationseconds, cheeractions.userid, userids.username FROM cheeractions
                INNER JOIN userids ON cheeractions.userid = userids.userid
                WHERE cheeractions.userid = $1
                LIMIT 1
            ''',
            actionId
        )

        await connection.close()

        if not utils.hasItems(record):
            return None

        return CheerAction(
            actionRequirement = CheerActionRequirement.fromStr(record[0]),
            actionType = CheerActionType.fromStr(record[1]),
            amount = record[2],
            durationSeconds = record[3],
            userId = record[4],
            userName = record[5]
        )

    async def getActions(self, userId: str) -> List[CheerAction]:
        if not utils.isValidStr(userId):
            raise ValueError(f'userId argument is malformed: \"{userId}\"')

        if userId in self.__cache:
            return self.__cache[userId]

        connection = await self.__getDatabaseConnection()
        records = await connection.fetchRows(
            '''
                SELECT cheeractions.actiontype, cheeractions.amount, cheeractions.durationseconds, cheeractions.userid, userids.username FROM cheeractions
                INNER JOIN userids ON cheeractions.userid = userids.userid
                WHERE cheeractions.userid = $1
                ORDER BY cheeractions.amount DESC
            ''',
            userId
        )

        await connection.close()
        actions: List[CheerAction] = list()

        for record in records:
            actions.append(CheerAction(
                actionRequirement = CheerActionRequirement.fromStr(record[0]),
                actionType = CheerActionType.fromStr(record[1]),
                amount = record[2],
                durationSeconds = record[3],
                userId = record[4],
                userName = record[5]
            ))

        self.__cache[userId] = actions
        return actions

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
                    CREATE TABLE IF NOT EXISTS cheeractions (
                        actionid public.citext NOT NULL PRIMARY KEY,
                        actionrequirement text NOT NULL,
                        actiontype text NOT NULL,
                        amount integer NOT NULL,
                        durationseconds integer DEFAULT NULL,
                        userid public.citext NOT NULL
                    )
                '''
            )
        elif connection.getDatabaseType() is DatabaseType.SQLITE:
            await connection.createTableIfNotExists(
                '''
                    CREATE TABLE IF NOT EXISTS cheeractions (
                        actionid TEXT NOT NULL PRIMARY KEY COLLATE NOCASE,
                        actionrequirement TEXT NOT NULL,
                        actiontype TEXT NOT NULL,
                        amount INTEGER NOT NULL,
                        durationseconds INTEGER DEFAULT NULL,
                        userid TEXT NOT NULL COLLATE NOCASE
                    )
                '''
            )
        else:
            raise RuntimeError(f'Encountered unexpected DatabaseType when trying to create tables: \"{connection.getDatabaseType()}\"')

        await connection.close()

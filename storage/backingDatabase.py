try:
    from CynanBotCommon.storage.databaseConnection import DatabaseConnection
    from CynanBotCommon.storage.databaseType import DatabaseType
except:
    from storage.databaseConnection import DatabaseConnection
    from storage.databaseType import DatabaseType


class BackingDatabase():

    async def getConnection(self) -> DatabaseConnection:
        pass

    def getDatabaseType(self) -> DatabaseType:
        pass

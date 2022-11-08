from typing import Any, List, Optional

try:
    from CynanBotCommon.storage.databaseType import DatabaseType
except:
    from storage.databaseType import DatabaseType


class DatabaseConnection():

    async def close(self):
        pass

    async def execute(self, query: str, *args: Optional[Any]):
        pass

    async def fetchRow(self, query: str, *args: Optional[Any]) -> Optional[List[Any]]:
        pass

    async def fetchRows(self, query: str, *args: Optional[Any]) -> Optional[List[List[Any]]]:
        pass

    def getDatabaseType(self) -> DatabaseType:
        pass

    def isClosed(self) -> bool:
        pass

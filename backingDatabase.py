import aiosqlite
from aiosqlite import Connection

try:
    import CynanBotCommon.utils as utils
except:
    import utils


class BackingDatabase():

    def __init__(self, backingDatabaseFile: str = 'CynanBotCommon/database.sqlite'):
        if not utils.isValidStr(backingDatabaseFile):
            raise ValueError(f'backingDatabaseFile argument is malformed: \"{backingDatabaseFile}\"')

        self.__backingDatabaseFile: str = backingDatabaseFile

    async def getConnection(self) -> Connection:
        return await aiosqlite.connect(self.__backingDatabaseFile)

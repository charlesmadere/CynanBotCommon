import sqlite3

try:
    import CynanBotCommon.utils as utils
except:
    import utils


class BackingDatabase():

    def __init__(self, databaseFile: str = 'CynanBotCommon/database.sqlite'):
        if not utils.isValidStr(databaseFile):
            raise ValueError(f'databaseFile argument is malformed: \"{databaseFile}\"')

        self.__connection = sqlite3.connect(databaseFile)

    def getConnection(self):
        return self.__connection

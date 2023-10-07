from typing import Any, Dict, Optional

try:
    import CynanBotCommon.utils as utils
    from CynanBotCommon.clearable import Clearable
    from CynanBotCommon.storage.jsonReaderInterface import JsonReaderInterface
except:
    import utils
    from clearable import Clearable
    from storage.jsonReaderInterface import JsonReaderInterface


class PsqlCredentialsProvider(Clearable):

    def __init__(self, credentialsJsonReader: JsonReaderInterface):
        if not isinstance(credentialsJsonReader, JsonReaderInterface):
            raise ValueError(f'credentialsJsonReader argument is malformed: \"{credentialsJsonReader}\"')

        self.__credentialsJsonReader: JsonReaderInterface = credentialsJsonReader

        self.__jsonCache: Optional[Dict[str, Any]] = None

    async def clearCaches(self):
        self.__jsonCache = None

    async def __readJsonAsync(self) -> Dict[str, Any]:
        if self.__jsonCache is not None:
            return self.__jsonCache

        jsonCache = await self.__credentialsJsonReader.readJsonAsync()
        self.__jsonCache = jsonCache

        return jsonCache

    async def requireDatabaseName(self) -> str:
        jsonContents = await self.__readJsonAsync()
        return utils.getStrFromDict(jsonContents, 'databaseName')

    async def requireMaxConnectionsSize(self) -> int:
        jsonContents = await self.__readJsonAsync()
        return utils.getIntFromDict(jsonContents, 'maxConnectionsSize', fallback = 100)

    async def requireUser(self) -> str:
        jsonContents = await self.__readJsonAsync()
        return utils.getStrFromDict(jsonContents, 'user')

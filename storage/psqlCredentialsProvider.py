import json
from typing import Any, Dict, Optional

import aiofiles
import aiofiles.ospath

try:
    import CynanBotCommon.utils as utils
except:
    import utils


class PsqlCredentialsProvider():

    def __init__(self, credentialsFile: str = 'CynanBotCommon/storage/psqlCredentials.json'):
        if not utils.isValidStr(credentialsFile):
            raise ValueError(f'credentialsFile argument is malformed: \"{credentialsFile}\"')

        self.__credentialsFile: str = credentialsFile
        self.__jsonCache: Optional[Dict[str, Any]] = None

    async def clearCaches(self):
        self.__jsonCache = None

    async def __readJsonAsync(self) -> Dict[str, Any]:
        if self.__jsonCache is not None:
            return self.__jsonCache

        if not await aiofiles.ospath.exists(self.__credentialsFile):
            raise FileNotFoundError(f'Credentials file not found: \"{self.__credentialsFile}\"')

        async with aiofiles.open(self.__credentialsFile, mode = 'r') as file:
            data = await file.read()
            jsonContents = json.loads(data)

        if jsonContents is None:
            raise IOError(f'Error reading from credentials file: \"{self.__credentialsFile}\"')
        elif len(jsonContents) == 0:
            raise ValueError(f'JSON contents of credentials file \"{self.__credentialsFile}\" is empty')

        self.__jsonCache = jsonContents
        return jsonContents

    async def requireDatabaseName(self) -> str:
        jsonContents = await self.__readJsonAsync()
        return utils.getStrFromDict(jsonContents, 'databaseName')

    async def requireUser(self) -> str:
        jsonContents = await self.__readJsonAsync()
        return utils.getStrFromDict(jsonContents, 'user')

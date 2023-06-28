import json
import os
from typing import Any, Dict, Optional

import aiofiles
import aiofiles.ospath

try:
    import CynanBotCommon.utils as utils
    from CynanBotCommon.storage.jsonReaderInterface import JsonReaderInterface
except:
    import utils
    from storage.jsonReaderInterface import JsonReaderInterface


class JsonFileReader(JsonReaderInterface):

    def __init__(self, fileName: str):
        if not utils.isValidStr(fileName):
            raise ValueError(f'fileName argument is malformed: \"{fileName}\"')

        self.__fileName: str = fileName

    def readJson(self) -> Optional[Dict[Any, Any]]:
        if not os.path.exists(self.__fileName):
            raise FileNotFoundError(f'File not found: \"{self.__fileName}\"')

        jsonContents: Optional[Dict[Any, Any]] = None

        with open(self.__fileName, 'r') as file:
            jsonContents = json.load(file)

        return jsonContents

    async def readJsonAsync(self) -> Optional[Dict[Any, Any]]:
        if not await aiofiles.ospath.exists(self.__fileName):
            raise FileNotFoundError(f'File not found: \"{self.__fileName}\"')

        jsonContents: Optional[Dict[Any, Any]] = None

        async with aiofiles.open(self.__fileName, mode = 'r') as file:
            data = await file.read()
            jsonContents = json.loads(data)

        return jsonContents

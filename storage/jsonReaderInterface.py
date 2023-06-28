from typing import Any, Dict, Optional


class JsonReaderInterface():

    def deleteFile(self):
        pass

    async def deleteFileAsync(self):
        pass

    def fileExists(self) -> bool:
        pass

    async def fileExistsAsync(self) -> bool:
        pass

    def readJson(self) -> Optional[Dict[Any, Any]]:
        pass

    async def readJsonAsync(self) -> Optional[Dict[Any, Any]]:
        pass

from typing import Any, Dict, Optional


class JsonReaderInterface():

    def readJson(self) -> Optional[Dict[Any, Any]]:
        pass

    async def readJsonAsync(self) -> Optional[Dict[Any, Any]]:
        pass

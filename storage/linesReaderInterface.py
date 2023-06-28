from typing import List, Optional


class LinesReaderInterface():

    def readLines(self) -> Optional[List[str]]:
        pass

    async def readLinesAsync(self) -> Optional[List[str]]:
        pass

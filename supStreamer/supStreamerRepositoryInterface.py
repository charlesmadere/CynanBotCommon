from abc import abstractmethod
from typing import Optional

try:
    from CynanBotCommon.clearable import Clearable
    from CynanBotCommon.supStreamer.supStreamerAction import SupStreamerAction
except:
    from clearable import Clearable
    from supStreamer.supStreamerAction import SupStreamerAction
    

class SupStreamerRepositoryInterface(Clearable):

    @abstractmethod
    async def get(self, broadcasterUserId: str) -> Optional[SupStreamerAction]:
        pass

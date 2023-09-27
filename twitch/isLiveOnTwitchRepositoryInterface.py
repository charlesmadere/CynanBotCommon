from abc import abstractmethod
from typing import Dict, List

try:
    from CynanBotCommon.clearable import Clearable
except:
    from clearable import Clearable


class IsLiveOnTwitchRepositoryInterface(Clearable):

    @abstractmethod
    async def isLive(self, twitchHandles: List[str]) -> Dict[str, bool]:
        pass

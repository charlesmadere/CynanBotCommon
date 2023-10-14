from abc import abstractmethod
from typing import Set

try:
    from CynanBotCommon.clearable import Clearable
except:
    from clearable import Clearable


class TwitchWebsocketAllowedUserIdsRepositoryInterface(Clearable):

    @abstractmethod
    async def getUserIds(self) -> Set[str]:
        pass

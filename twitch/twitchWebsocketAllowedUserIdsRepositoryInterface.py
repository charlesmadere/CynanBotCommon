from abc import ABC, abstractmethod
from typing import List


class TwitchWebsocketAllowedUserIdsRepositoryInterface(ABC):

    @abstractmethod
    async def getUserIds(self) -> List[str]:
        pass

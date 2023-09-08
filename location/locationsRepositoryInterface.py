from abc import ABC, abstractmethod

try:
    from CynanBotCommon.location.location import Location
except:
    from location.location import Location


class LocationsRepositoryInterface(ABC):

    @abstractmethod
    async def clearCaches(self):
        pass

    @abstractmethod
    async def getLocation(self, locationId: str) -> Location:
        pass

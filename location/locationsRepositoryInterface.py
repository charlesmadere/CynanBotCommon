from abc import abstractmethod

try:
    from CynanBotCommon.clearable import Clearable
    from CynanBotCommon.location.location import Location
except:
    from clearable import Clearable
    from location.location import Location


class LocationsRepositoryInterface(Clearable):

    @abstractmethod
    async def getLocation(self, locationId: str) -> Location:
        pass

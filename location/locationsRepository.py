import json
from os import path
from typing import Dict

from aiofile import async_open

try:
    import CynanBotCommon.utils as utils
    from CynanBotCommon.location.location import Location
    from CynanBotCommon.timeZoneRepository import TimeZoneRepository
except:
    import utils
    from timeZoneRepository import TimeZoneRepository

    from location.location import Location


class LocationsRepository():

    def __init__(
        self,
        timeZoneRepository: TimeZoneRepository,
        locationsFile: str = 'CynanBotCommon/location/locationsRepository.json'
    ):
        if timeZoneRepository is None:
            raise ValueError(f'timeZoneRepository argument is malformed: \"{timeZoneRepository}\"')
        elif not utils.isValidStr(locationsFile):
            raise ValueError(f'locationsFile argument is malformed: \"{locationsFile}\"')

        self.__timeZoneRepository: TimeZoneRepository = timeZoneRepository
        self.__locationsFile: str = locationsFile
        self.__locationsCache: Dict[str, Location] = dict()

    async def getLocation(self, locationId: str) -> Location:
        if not utils.isValidStr(locationId):
            raise ValueError(f'locationId argument is malformed: \"{locationId}\"')

        locationId = locationId.lower()

        if locationId in self.__locationsCache:
            return self.__locationsCache[locationId]

        jsonContents = await self.__readAllJson()

        for _id in jsonContents:
            if _id.lower() == locationId:
                timeZoneStr = jsonContents[_id]['timeZone']
                timeZone = self.__timeZoneRepository.getTimeZone(timeZoneStr)

                location = Location(
                    latitude = jsonContents[_id]['lat'],
                    longitude = jsonContents[_id]['lon'],
                    locationId = _id,
                    name = jsonContents[_id]['name'],
                    timeZone = timeZone
                )

                self.__locationsCache[_id.lower()] = location
                return location

        raise RuntimeError(f'Unable to find location with ID \"{locationId}\" in locations file: \"{self.__locationsFile}\"')

    async def __readAllJson(self) -> Dict[str, object]:
        if not path.exists(self.__locationsFile):
            raise FileNotFoundError(f'Locations file not found: \"{self.__locationsFile}\"')

        async with async_open(self.__locationsFile, 'r') as file:
            data = await file.read()
            jsonContents = json.loads(data)

        if jsonContents is None:
            raise IOError(f'Error reading from locations file: \"{self.__locationsFile}\"')
        elif len(jsonContents) == 0:
            raise ValueError(f'JSON contents of locations file \"{self.__locationsFile}\" is empty')

        return jsonContents

import json
from os import path

import CynanBotCommon.utils as utils
from CynanBotCommon.location import Location
from CynanBotCommon.timeZoneRepository import TimeZoneRepository


class LocationsRepository():

    def __init__(
        self,
        timeZoneRepository: TimeZoneRepository,
        locationsFile: str = 'CynanBotCommon/locationsRepository.json'
    ):
        if not utils.isValidStr(locationsFile):
            raise ValueError(f'locationsFile argument is malformed: \"{locationsFile}\"')
        elif timeZoneRepository is None:
            raise ValueError(f'timeZoneRepository argument is malformed: \"{timeZoneRepository}\"')

        self.__locationsCache = dict()
        self.__locationsFile = locationsFile
        self.__timeZoneRepository = timeZoneRepository

    def getLocation(self, id_: str) -> Location:
        if not utils.isValidStr(id_):
            raise ValueError(f'id_ argument is malformed: \"{id_}\"')

        if id_.lower() in self.__locationsCache:
            return self.__locationsCache[id_.lower()]

        if not path.exists(self.__locationsFile):
            raise FileNotFoundError(f'Locations file not found: \"{self.__locationsFile}\"')

        with open(self.__locationsFile, 'r') as file:
            jsonContents = json.load(file)

        if jsonContents is None:
            raise IOError(f'Error reading from locations file: \"{self.__locationsFile}\"')
        elif len(jsonContents) == 0:
            raise ValueError(f'JSON contents of locations file \"{self.__locationsFile}\" is empty')

        for locationId in jsonContents:
            if id_.lower() == locationId.lower():
                timeZoneStr = jsonContents[locationId]['timeZone']
                timeZone = self.__timeZoneRepository.getTimeZone(timeZoneStr)

                location = Location(
                    lat = jsonContents[locationId]['lat'],
                    lon = jsonContents[locationId]['lon'],
                    id_ = locationId,
                    name = jsonContents[locationId]['name'],
                    timeZone = timeZone
                )

                self.__locationsCache[id_.lower()] = location
                return location

        raise RuntimeError(f'Unable to find location with ID \"{id_}\" in locations file: \"{self.__locationsFile}\"')

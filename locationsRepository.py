import json
from os import path
from typing import Dict

import CynanBotCommon.utils as utils
from CynanBotCommon.location import Location
from CynanBotCommon.timeZoneRepository import TimeZoneRepository


class LocationsRepository():

    def __init__(
        self,
        timeZoneRepository: TimeZoneRepository,
        locationsFile: str = 'CynanBotCommon/locationsRepository.json'
    ):
        if timeZoneRepository is None:
            raise ValueError(f'timeZoneRepository argument is malformed: \"{timeZoneRepository}\"')
        elif not utils.isValidStr(locationsFile):
            raise ValueError(f'locationsFile argument is malformed: \"{locationsFile}\"')

        self.__timeZoneRepository = timeZoneRepository
        self.__locationsFile = locationsFile

        self.__locationsCache = dict()

    def getLocation(self, locationId: str) -> Location:
        if not utils.isValidStr(locationId):
            raise ValueError(f'locationId argument is malformed: \"{locationId}\"')

        if locationId.lower() in self.__locationsCache:
            return self.__locationsCache[locationId.lower()]

        jsonContents = self.__readJson()

        for locationId in jsonContents:
            if locationId.lower() == locationId.lower():
                timeZoneStr = jsonContents[locationId]['timeZone']
                timeZone = self.__timeZoneRepository.getTimeZone(timeZoneStr)

                location = Location(
                    latitude = jsonContents[locationId]['lat'],
                    longitude = jsonContents[locationId]['lon'],
                    locationId = locationId,
                    name = jsonContents[locationId]['name'],
                    timeZone = timeZone
                )

                self.__locationsCache[locationId.lower()] = location
                return location

        raise RuntimeError(f'Unable to find location with ID \"{locationId}\" in locations file: \"{self.__locationsFile}\"')

    def __readJson(self) -> Dict:
        if not path.exists(self.__locationsFile):
            raise FileNotFoundError(f'Locations file not found: \"{self.__locationsFile}\"')

        with open(self.__locationsFile, 'r') as file:
            jsonContents = json.load(file)

        if jsonContents is None:
            raise IOError(f'Error reading from locations file: \"{self.__locationsFile}\"')
        elif len(jsonContents) == 0:
            raise ValueError(f'JSON contents of locations file \"{self.__locationsFile}\" is empty')

        return jsonContents

from datetime import tzinfo

import CynanBotCommon.utils as utils


class Location():

    def __init__(self, lat: float, lon: float, id_: str, name: str, timeZone: tzinfo):
        if not utils.isValidNum(lat):
            raise ValueError(f'lat argument is malformed: \"{lat}\"')
        elif not utils.isValidNum(lon):
            raise ValueError(f'lon argument is malformed: \"{lon}\"')
        elif not utils.isValidStr(id_):
            raise ValueError(f'id_ argument is malformed: \"{id_}\"')
        elif not utils.isValidStr(name):
            raise ValueError(f'name argument is malformed: \"{name}\"')
        elif timeZone is None:
            raise ValueError(f'timeZone argument is malformed: \"{timeZone}\"')

        self.__id = id_
        self.__latitude = lat
        self.__longitude = lon
        self.__name = name
        self.__timeZone = timeZone

    def getId(self) -> str:
        return self.__id

    def getLatitude(self) -> float:
        return self.__latitude

    def getLongitude(self) -> float:
        return self.__longitude

    def getName(self) -> str:
        return self.__name

    def getTimeZone(self) -> tzinfo:
        return self.__timeZone

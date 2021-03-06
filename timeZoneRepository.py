from typing import List

import pytz

try:
    import CynanBotCommon.utils as utils
except:
    import utils


# A listing of pytz timezones can be found here:
# https://stackoverflow.com/questions/13866926/is-there-a-list-of-pytz-timezones

class TimeZoneRepository():

    def __init__(self):
        self.__timeZones = dict()

    def getTimeZone(self, timeZone: str):
        if not utils.isValidStr(timeZone):
            return None
        elif timeZone in self.__timeZones:
            return self.__timeZones[timeZone]

        newTimeZone = pytz.timezone(timeZone)
        self.__timeZones[timeZone] = newTimeZone
        return newTimeZone

    def getTimeZones(self, timeZones: List[str]):
        if not utils.hasItems(timeZones):
            return None

        newTimeZones = list()

        for timeZone in timeZones:
            newTimeZone = self.getTimeZone(timeZone)

            if newTimeZone is not None:
                newTimeZones.append(newTimeZone)

        if utils.hasItems(newTimeZones):
            return newTimeZones
        else:
            return None

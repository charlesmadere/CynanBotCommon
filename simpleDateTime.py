from datetime import datetime, timezone
from typing import Any


class SimpleDateTime():

    def __init__(
        self,
        now: datetime = None,
        timeZone: timezone = timezone.utc
    ):
        if now is None:
            if timeZone is None:
                raise ValueError('Both `now` and `timeZone` can\'t be `None`!')
            else:
                self.__now: datetime = datetime.now(timeZone)
        else:
            self.__now: datetime = now

    def getDateTime(self) -> datetime:
        return self.__now

    def getDateAndTimeStr(self) -> str:
        return f'{self.getYearMonthDayStr()} {self.getTimeStr()}'

    def getDayStr(self) -> str:
        return self.__now.strftime('%d')

    def getHourStr(self) -> str:
        return self.__now.strftime('%H')

    def getIsoFormatStr(self) -> str:
        return self.__now.isoformat()

    def getMinuteStr(self) -> str:
        return self.__now.strftime('%M')

    def getMonthStr(self) -> str:
        return self.__now.strftime('%m')

    def getMonthInt(self) -> int:
        return self.__now.month

    def getSecondStr(self) -> str:
        return self.__now.strftime('%S')

    def getTimeStr(self) -> str:
        return f'{self.getHourStr()}:{self.getMinuteStr()}:{self.getSecondStr()}'

    def getYearInt(self) -> int:
        return self.__now.year

    def getYearStr(self) -> str:
        return self.__now.strftime('%Y')

    def getYearMonthDayStr(self) -> str:
        return f'{self.getYearStr()}/{self.getMonthStr()}/{self.getDayStr()}'

    def __lt__(self, other: Any) -> bool:
        if isinstance(other, SimpleDateTime):
            return self.__now < other.__now
        else:
            return False

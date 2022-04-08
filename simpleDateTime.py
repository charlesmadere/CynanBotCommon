from datetime import datetime, timezone


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

        self.__year: str = self.__now.strftime('%Y')
        self.__month: str = self.__now.strftime('%m')
        self.__day: str = self.__now.strftime('%d')
        self.__hour: str = self.__now.strftime('%H')
        self.__minute: str = self.__now.strftime('%M')
        self.__second: str = self.__now.strftime('%S')

    def getDateTime(self) -> datetime:
        return self.__now

    def getDateAndTimeStr(self) -> str:
        return f'{self.getYearMonthDayStr()} {self.getTimeStr()}'

    def getDay(self) -> str:
        return self.__day

    def getHour(self) -> str:
        return self.__hour

    def getMinute(self) -> str:
        return self.__minute

    def getMonth(self) -> str:
        return self.__month

    def getMonthInt(self) -> int:
        return self.__now.month

    def getSecond(self) -> str:
        return self.__second

    def getTimeStr(self) -> str:
        return f'{self.getHour()}:{self.getMinute()}:{self.getSecond()}'

    def getYear(self) -> str:
        return self.__year

    def getYearInt(self) -> int:
        return self.__now.year

    def getYearMonthDayStr(self) -> str:
        return f'{self.getYear()}/{self.getMonth()}/{self.getDay()}'

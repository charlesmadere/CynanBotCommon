import locale
from typing import List

import CynanBotCommon.utils as utils


class WeatherReport():

    def __init__(
        self,
        airQuality: int,
        humidity: int,
        pressure: int,
        temperature: float,
        tomorrowsHighTemperature: float,
        tomorrowsLowTemperature: float,
        alerts: List[str],
        conditions: List[str],
        tomorrowsConditions: List[str]
    ):
        if not utils.isValidNum(humidity):
            raise ValueError(f'humidity argument is malformed: \"{humidity}\"')
        elif not utils.isValidNum(pressure):
            raise ValueError(f'pressure argument is malformed: \"{pressure}\"')
        elif not utils.isValidNum(temperature):
            raise ValueError(f'temperature argument is malformed: \"{temperature}\"')
        elif not utils.isValidNum(tomorrowsHighTemperature):
            raise ValueError(f'tomorrowsHighTemperature argument is malformed: \"{tomorrowsHighTemperature}\"')
        elif not utils.isValidNum(tomorrowsLowTemperature):
            raise ValueError(f'tomorrowsLowTemperature argument is malformed: \"{tomorrowsLowTemperature}\"')

        self.__airQuality = airQuality
        self.__humidity = humidity
        self.__pressure = pressure
        self.__temperature = temperature
        self.__tomorrowsHighTemperature = tomorrowsHighTemperature
        self.__tomorrowsLowTemperature = tomorrowsLowTemperature
        self.__alerts = alerts
        self.__conditions = conditions
        self.__tomorrowsConditions = tomorrowsConditions

    def __cToF(self, celsius: float) -> float:
        return (celsius * (9 / 5)) + 32

    def getAirQuality(self) -> int:
        return self.__airQuality

    def getAirQualityStr(self) -> str:
        return locale.format_string("%d", self.getAirQuality(), grouping = True)

    def getAlerts(self) -> List[str]:
        return self.__alerts

    def getConditions(self) -> List[str]:
        return self.__conditions

    def getHumidity(self) -> int:
        return self.__humidity

    def getPressure(self) -> int:
        return self.__pressure

    def getPressureStr(self) -> str:
        return locale.format_string("%d", self.getPressure(), grouping = True)

    def getTemperature(self):
        return int(round(self.__temperature))

    def getTemperatureStr(self):
        return locale.format_string("%d", self.getTemperature(), grouping = True)

    def getTemperatureImperial(self):
        return int(round(self.__cToF(self.__temperature)))

    def getTemperatureImperialStr(self):
        return locale.format_string("%d", self.getTemperatureImperial(), grouping = True)

    def getTomorrowsConditions(self) -> List[str]:
        return self.__tomorrowsConditions

    def getTomorrowsLowTemperature(self) -> int:
        return int(round(self.__tomorrowsLowTemperature))

    def getTomorrowsLowTemperatureStr(self) -> str:
        return locale.format_string("%d", self.getTomorrowsLowTemperature(), grouping = True)

    def getTomorrowsLowTemperatureImperial(self) -> int:
        return int(round(self.__cToF(self.__tomorrowsLowTemperature)))

    def getTomorrowsLowTemperatureImperialStr(self) -> str:
        return locale.format_string("%d", self.getTomorrowsLowTemperatureImperial(), grouping = True)

    def getTomorrowsHighTemperature(self) -> int:
        return int(round(self.__tomorrowsHighTemperature))

    def getTomorrowsHighTemperatureStr(self) -> str:
        return locale.format_string("%d", self.getTomorrowsHighTemperature(), grouping = True)

    def getTomorrowsHighTemperatureImperial(self) -> int:
        return int(round(self.__cToF(self.__tomorrowsHighTemperature)))

    def getTomorrowsHighTemperatureImperialStr(self) -> str:
        return locale.format_string("%d", self.getTomorrowsHighTemperatureImperial(), grouping = True)

    def hasAirQuality(self) -> bool:
        return utils.isValidNum(self.__airQuality)

    def hasAlerts(self) -> bool:
        return utils.hasItems(self.__alerts)

    def hasConditions(self) -> bool:
        return utils.hasItems(self.__conditions)

    def hasTomorrowsConditions(self) -> bool:
        return utils.hasItems(self.__tomorrowsConditions)

    def toStr(self, delimiter: str = ', ') -> str:
        if delimiter is None:
            raise ValueError(f'delimiter argument is malformed: \"{delimiter}\"')

        temperature = f'🌡 Temperature is {self.getTemperatureStr()}°C ({self.getTemperatureImperialStr()}°F), '
        humidity = f'humidity is {self.getHumidity()}%, '

        airQuality = ''
        if self.hasAirQuality():
            airQuality = f'air quality is {self.getAirQualityStr()}, '

        pressure = f'and pressure is {self.getPressureStr()} hPa. '

        conditions = ''
        if self.hasConditions():
            conditionsJoin = delimiter.join(self.getConditions())
            conditions = f'Current conditions: {conditionsJoin}. '

        tomorrowsTemps = f'Tomorrow has a low of {self.getTomorrowsLowTemperatureStr()}°C ({self.getTomorrowsLowTemperatureImperialStr()}°F) and a high of {self.getTomorrowsHighTemperatureStr()}°C ({self.getTomorrowsHighTemperatureImperialStr()}°F). '

        tomorrowsConditions = ''
        if self.hasTomorrowsConditions():
            tomorrowsConditionsJoin = delimiter.join(self.getTomorrowsConditions())
            tomorrowsConditions = f'Tomorrow\'s conditions: {tomorrowsConditionsJoin}. '

        alerts = ''
        if self.hasAlerts():
            alertsJoin = ' '.join(self.getAlerts())
            alerts = f'🚨 {alertsJoin}'

        return f'{temperature}{humidity}{airQuality}{pressure}{conditions}{tomorrowsTemps}{tomorrowsConditions}{alerts}'

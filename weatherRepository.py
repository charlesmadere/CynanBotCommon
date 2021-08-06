import locale
from datetime import timedelta
from enum import Enum, auto
from json.decoder import JSONDecodeError
from typing import Dict, List

import requests
from requests import ConnectionError, HTTPError, Timeout
from urllib3.exceptions import MaxRetryError, NewConnectionError

try:
    import CynanBotCommon.utils as utils
    from CynanBotCommon.location import Location
    from CynanBotCommon.timedDict import TimedDict
except:
    import utils
    from location import Location
    from timedDict import TimedDict


class AirQualityIndex(Enum):

    FAIR = auto()
    GOOD = auto()
    MODERATE = auto()
    POOR = auto()
    VERY_POOR = auto()

    @classmethod
    def fromInt(cls, airQualityIndex: int):
        if not utils.isValidNum(airQualityIndex):
            raise ValueError(f'airQualityIndex argument is malformed: \"{airQualityIndex}\"')

        if airQualityIndex == 1:
            return AirQualityIndex.GOOD
        elif airQualityIndex == 2:
            return AirQualityIndex.FAIR
        elif airQualityIndex == 3:
            return AirQualityIndex.MODERATE
        elif airQualityIndex == 4:
            return AirQualityIndex.POOR
        elif airQualityIndex == 5:
            return AirQualityIndex.VERY_POOR
        else:
            raise ValueError(f'unknown AirQualityIndex: \"{airQualityIndex}\"')

    def toStr(self) -> str:
        if self is AirQualityIndex.FAIR:
            return 'fair'
        elif self is AirQualityIndex.GOOD:
            return 'good'
        elif self is AirQualityIndex.MODERATE:
            return 'moderate'
        elif self is AirQualityIndex.POOR:
            return 'poor'
        elif self is AirQualityIndex.VERY_POOR:
            return 'very poor'
        else:
            raise RuntimeError(f'unknown AirQualityIndex: \"{self}\"')


class UvIndex(Enum):

    LOW = auto()
    MODERATE_TO_HIGH = auto()
    VERY_HIGH_TO_EXTREME = auto()

    @classmethod
    def fromFloat(cls, uvIndex: float):
        if not utils.isValidNum(uvIndex):
            raise ValueError(f'uvIndex argument is malformed: \"{uvIndex}\"')

        if uvIndex <= 2:
            return UvIndex.LOW
        elif uvIndex <= 7:
            return UvIndex.MODERATE_TO_HIGH
        else:
            return UvIndex.VERY_HIGH_TO_EXTREME

    def toStr(self) -> str:
        if self is UvIndex.LOW:
            return 'low'
        elif self is UvIndex.MODERATE_TO_HIGH:
            return 'moderate to high'
        elif self is UvIndex.VERY_HIGH_TO_EXTREME:
            return 'very high to extreme'
        else:
            raise RuntimeError(f'unknown UvIndex: \"{self}\"')


class WeatherReport():

    def __init__(
        self,
        airQualityIndex: AirQualityIndex,
        humidity: int,
        pressure: int,
        temperature: float,
        tomorrowsHighTemperature: float,
        tomorrowsLowTemperature: float,
        alerts: List[str],
        conditions: List[str],
        tomorrowsConditions: List[str],
        uvIndex: UvIndex
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

        self.__airQualityIndex = airQualityIndex
        self.__humidity = humidity
        self.__pressure = pressure
        self.__temperature = temperature
        self.__tomorrowsHighTemperature = tomorrowsHighTemperature
        self.__tomorrowsLowTemperature = tomorrowsLowTemperature
        self.__alerts = alerts
        self.__conditions = conditions
        self.__tomorrowsConditions = tomorrowsConditions
        self.__uvIndex = uvIndex

    def __cToF(self, celsius: float) -> float:
        return (celsius * (9 / 5)) + 32

    def getAirQualityIndex(self) -> AirQualityIndex:
        return self.__airQualityIndex

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

    def getUvIndex(self) -> UvIndex:
        return self.__uvIndex

    def hasAirQualityIndex(self) -> bool:
        return self.__airQualityIndex is not None

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

        uvIndex = ''
        if self.__uvIndex is UvIndex.MODERATE_TO_HIGH or self.__uvIndex is UvIndex.VERY_HIGH_TO_EXTREME:
            uvIndex = f'UV Index is {self.__uvIndex.toStr()}, '

        airQuality = ''
        if self.hasAirQualityIndex():
            airQuality = f'air quality index is {self.__airQualityIndex.toStr()}, '

        pressure = f'and pressure is {self.getPressureStr()} hPa. '

        conditions = ''
        if self.hasConditions():
            conditionsJoin = delimiter.join(self.__conditions)
            conditions = f'Current conditions: {conditionsJoin}. '

        tomorrowsTemps = f'Tomorrow has a low of {self.getTomorrowsLowTemperatureStr()}°C ({self.getTomorrowsLowTemperatureImperialStr()}°F) and a high of {self.getTomorrowsHighTemperatureStr()}°C ({self.getTomorrowsHighTemperatureImperialStr()}°F). '

        tomorrowsConditions = ''
        if self.hasTomorrowsConditions():
            tomorrowsConditionsJoin = delimiter.join(self.__tomorrowsConditions)
            tomorrowsConditions = f'Tomorrow\'s conditions: {tomorrowsConditionsJoin}. '

        alerts = ''
        if self.hasAlerts():
            alertsJoin = ' '.join(self.__alerts)
            alerts = f'🚨 {alertsJoin}'

        return f'{temperature}{humidity}{uvIndex}{airQuality}{pressure}{conditions}{tomorrowsTemps}{tomorrowsConditions}{alerts}'


class WeatherRepository():

    def __init__(
        self,
        oneWeatherApiKey: str,
        cacheTimeDelta: timedelta = timedelta(minutes = 20)
    ):
        if not utils.isValidStr(oneWeatherApiKey):
            raise ValueError(f'oneWeatherApiKey argument is malformed: \"{oneWeatherApiKey}\"')
        elif cacheTimeDelta is None:
            raise ValueError(f'cacheTimeDelta argument is malformed: \"{cacheTimeDelta}\"')

        self.__oneWeatherApiKey = oneWeatherApiKey
        self.__cache = TimedDict(timeDelta = cacheTimeDelta)
        self.__conditionIcons = self.__createConditionIconsDict()

    def __chooseTomorrowFromForecast(self, jsonResponse: dict):
        currentSunrise = jsonResponse['current']['sunrise']
        currentSunset = jsonResponse['current']['sunset']

        for dayJson in jsonResponse['daily']:
            if dayJson['sunrise'] > currentSunrise and dayJson['sunset'] > currentSunset:
                return dayJson

        raise RuntimeError(f'Unable to find viable tomorrow data in JSON response: \"{jsonResponse}\"')

    def __createConditionIconsDict(self) -> Dict[str, str]:
        # This dictionary is built from the Weather Condition Codes listed here:
        # https://openweathermap.org/weather-conditions#Weather-Condition-Codes-2

        icons: Dict[str, str] = dict()
        icons['200'] = '⛈️'
        icons['201'] = icons['200']
        icons['202'] = icons['200']
        icons['210'] = '🌩️'
        icons['211'] = icons['210']
        icons['212'] = icons['211']
        icons['221'] = icons['200']
        icons['230'] = icons['200']
        icons['231'] = icons['200']
        icons['232'] = icons['200']
        icons['300'] = '☔'
        icons['301'] = icons['300']
        icons['310'] = icons['300']
        icons['311'] = icons['300']
        icons['313'] = icons['300']
        icons['500'] = icons['300']
        icons['501'] = '🌧️'
        icons['502'] = icons['501']
        icons['503'] = icons['501']
        icons['504'] = icons['501']
        icons['520'] = icons['501']
        icons['521'] = icons['501']
        icons['522'] = icons['501']
        icons['531'] = icons['501']
        icons['600'] = '❄️'
        icons['601'] = icons['600']
        icons['602'] = '🌨️'
        icons['711'] = '🌫️'
        icons['721'] = icons['711']
        icons['731'] = icons['711']
        icons['741'] = icons['711']
        icons['762'] = '🌋'
        icons['771'] = '🌬'
        icons['781'] = '🌪️'
        icons['801'] = '☁️'
        icons['802'] = icons['801']
        icons['803'] = icons['801']
        icons['804'] = icons['801']

        return icons

    def __fetchAirQualityIndex(self, location: Location) -> AirQualityIndex:
        if location is None:
            raise ValueError(f'location argument is malformed: \"{location}\"')

        # Retrieve air quality index from: https://openweathermap.org/api/air-pollution
        # Doing this requires an API key, which you can get here: https://openweathermap.org/api

        requestUrl = 'https://api.openweathermap.org/data/2.5/air_pollution?appid={}&lat={}&lon={}'.format(
            self.__oneWeatherApiKey, location.getLatitude(), location.getLongitude())

        rawResponse = None
        try:
            rawResponse = requests.get(url = requestUrl, timeout = utils.getDefaultTimeout())
        except (ConnectionError, HTTPError, MaxRetryError, NewConnectionError, Timeout) as e:
            print(f'Exception occurred when attempting to fetch air quality index from Open Weather for \"{location.getLocationId()}\": {e}')
            raise RuntimeError(f'Exception occurred when attempting to fetch air quality index from Open Weather for \"{location.getLocationId()}\": {e}')

        jsonResponse = None
        try:
            jsonResponse = rawResponse.json()
        except JSONDecodeError as e:
            print(f'Exception occurred when attempting to decode Open Weather\'s air quality index response into JSON for \"{location.getLocationId()}\": {e}')
            raise RuntimeError(f'Exception occurred when attempting to decode Open Weather\'s air quality index response into JSON for \"{location.getLocationId()}\": {e}')

        airQualityIndex = utils.getIntFromDict(
            d = jsonResponse['list'][0]['main'],
            key = 'aqi'
        )

        return AirQualityIndex.fromInt(airQualityIndex)

    def fetchWeather(self, location: Location) -> WeatherReport:
        if location is None:
            raise ValueError(f'location argument is malformed: \"{location}\"')

        cacheValue = self.__cache[location.getLocationId()]
        if cacheValue is not None:
            return cacheValue

        weatherReport = self.__fetchWeather(location)
        self.__cache[location.getLocationId()] = weatherReport

        return weatherReport

    def __fetchWeather(self, location: Location) -> WeatherReport:
        if location is None:
            raise ValueError(f'location argument is malformed: \"{location}\"')

        print(f'Refreshing weather for \"{location.getName()}\" ({location.getLocationId()})... ({utils.getNowTimeText()})')

        # Retrieve weather report from https://openweathermap.org/api/one-call-api
        # Doing this requires an API key, which you can get here: https://openweathermap.org/api

        requestUrl = 'https://api.openweathermap.org/data/2.5/onecall?appid={}&lat={}&lon={}&exclude=minutely,hourly&units=metric'.format(
            self.__oneWeatherApiKey, location.getLatitude(), location.getLongitude())

        rawResponse = None
        try:
            rawResponse = requests.get(url = requestUrl, timeout = utils.getDefaultTimeout())
        except (ConnectionError, HTTPError, MaxRetryError, NewConnectionError, Timeout) as e:
            print(f'Exception occurred when attempting to fetch weather conditions from Open Weather for \"{location.getLocationId()}\": {e}')
            raise RuntimeError(f'Exception occurred when attempting to fetch weather conditions from Open Weather for \"{location.getLocationId()}\": {e}')
 
        jsonResponse = None
        try:
            jsonResponse = rawResponse.json()
        except JSONDecodeError as e:
            print(f'Exception occurred when attempting to decode Open Weather\'s response into JSON for \"{location.getLocationId()}\": {e}')
            raise RuntimeError(f'Exception occurred when attempting to decode Open Weather\'s response into JSON for \"{location.getLocationId()}\": {e}')

        currentJson = jsonResponse['current']
        humidity = currentJson['humidity']
        pressure = currentJson['pressure']
        temperature = currentJson['temp']
        uvIndex = UvIndex.fromFloat(utils.getFloatFromDict(currentJson, 'uvi'))

        conditions: List[str] = list()
        if 'weather' in currentJson and len(currentJson['weather']) >= 1:
            for conditionJson in currentJson['weather']:
                conditions.append(self.__prettifyCondition(conditionJson))

        alerts: List[str] = list()
        if 'alerts' in jsonResponse and len(jsonResponse['alerts']) >= 1:
            for alertJson in jsonResponse['alerts']:
                event = alertJson.get('event')
                senderName = alertJson.get('sender_name')

                if event is not None and len(event) >= 1:
                    if senderName is None or len(senderName) == 0:
                        alerts.append(f'Alert: {event}.')
                    else:
                        alerts.append(f'Alert from {senderName}: {event}.')

        tomorrowsJson = self.__chooseTomorrowFromForecast(jsonResponse)
        tomorrowsHighTemperature = tomorrowsJson['temp']['max']
        tomorrowsLowTemperature = tomorrowsJson['temp']['min']

        tomorrowsConditions: List[str] = list()
        if 'weather' in tomorrowsJson and len(tomorrowsJson['weather']) >= 1:
            for conditionJson in tomorrowsJson['weather']:
                tomorrowsConditions.append(conditionJson['description'])

        return WeatherReport(
            airQualityIndex = self.__fetchAirQualityIndex(location),
            humidity = int(round(humidity)),
            pressure = int(round(pressure)),
            temperature = temperature,
            tomorrowsHighTemperature = tomorrowsHighTemperature,
            tomorrowsLowTemperature = tomorrowsLowTemperature,
            alerts = alerts,
            conditions = conditions,
            tomorrowsConditions = tomorrowsConditions,
            uvIndex = uvIndex
        )

    def __prettifyCondition(self, conditionJson: dict) -> str:
        conditionIcon = ''
        if 'id' in conditionJson:
            id_ = str(conditionJson['id'])

            if id_ in self.__conditionIcons:
                icon = self.__conditionIcons[id_]
                conditionIcon = f'{icon} '

        conditionDescription = conditionJson['description']
        return f'{conditionIcon}{conditionDescription}'

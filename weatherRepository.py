from datetime import timedelta
from enum import Enum, auto
from json.decoder import JSONDecodeError

import requests
from requests import ConnectionError, HTTPError, Timeout
from urllib3.exceptions import MaxRetryError, NewConnectionError

try:
    import CynanBotCommon.utils as utils
    from CynanBotCommon.locationsRepository import Location
    from CynanBotCommon.timedDict import TimedDict
    from CynanBotCommon.weatherReport import WeatherReport
except:
    import utils
    from locationsRepository import Location
    from timedDict import TimedDict
    from weatherReport import WeatherReport


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


class WeatherRepository():

    def __init__(
        self,
        oneWeatherApiKey: str,
        cacheTimeDelta: timedelta = timedelta(hours = 1, minutes = 30)
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

    def __createConditionIconsDict(self):
        # This dictionary is built from the Weather Condition Codes listed here:
        # https://openweathermap.org/weather-conditions#Weather-Condition-Codes-2

        icons = dict()
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

        print(f'Refreshing weather for \"{location.getLocationId()}\"... ({utils.getNowTimeText()})')

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

        conditions = list()
        if 'weather' in currentJson and len(currentJson['weather']) >= 1:
            for conditionJson in currentJson['weather']:
                conditions.append(self.__prettifyCondition(conditionJson))

        alerts = list()
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

        tomorrowsConditions = list()
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
            tomorrowsConditions = tomorrowsConditions
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

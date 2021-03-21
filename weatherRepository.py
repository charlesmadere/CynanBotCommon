from datetime import timedelta
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


class WeatherRepository():

    def __init__(
        self,
        oneWeatherApiKey: str,
        iqAirApiKey: str = None,
        cacheTimeDelta: timedelta = timedelta(hours = 1, minutes = 30)
    ):
        if not utils.isValidStr(oneWeatherApiKey):
            raise ValueError(f'oneWeatherApiKey argument is malformed: \"{oneWeatherApiKey}\"')
        elif cacheTimeDelta is None:
            raise ValueError(f'cacheTimeDelta argument is malformed: \"{cacheTimeDelta}\"')

        if not utils.isValidStr(iqAirApiKey):
            print(f'IQAir API key is malformed: \"{iqAirApiKey}\". This won\'t prevent us from fetching weather, but it will prevent us from fetching the current air quality conditions at the given location.')

        self.__iqAirApiKey = iqAirApiKey
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

    def __fetchAirQuality(self, location: Location) -> int:
        if location is None:
            raise ValueError(f'location argument is malformed: \"{location}\"')

        # Retrieve air quality from: https://api-docs.iqair.com/
        # Doing this requires an API key, which you can get here:
        # https://www.iqair.com/us/commercial/air-quality-monitors/airvisual-platform/api

        requestUrl = 'https://api.airvisual.com/v2/nearest_city?key={}&lat={}&lon={}'.format(
            self.__iqAirApiKey, location.getLatitude(), location.getLongitude())

        rawResponse = None
        try:
            rawResponse = requests.get(url = requestUrl, timeout = utils.getDefaultTimeout())
        except (ConnectionError, HTTPError, MaxRetryError, NewConnectionError, Timeout) as e:
            print(f'Exception occurred when attempting to fetch air quality from IQAir for \"{location.getLocationId()}\": {e}')
            raise RuntimeError(f'Exception occurred when attempting to fetch air quality from IQAir for \"{location.getLocationId()}\": {e}')

        jsonResponse = None
        try:
            jsonResponse = rawResponse.json()
        except JSONDecodeError as e:
            print(f'Exception occurred when attempting to decode IQAir\'s response into JSON for \"{location.getLocationId()}\": {e}')
            raise RuntimeError(f'Exception occurred when attempting to decode IQAir\'s response into JSON for \"{location.getLocationId()}\": {e}')

        if jsonResponse.get('status') != 'success':
            print(f'IQAir\'s response \"status\" was not \"success\": {jsonResponse}')
            raise ValueError(f'IQAir\'s response \"status\" was not \"success\": {jsonResponse}')

        return utils.getIntFromDict(
            d = jsonResponse['data']['current']['pollution'],
            key = 'aqius'
        )

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
        # Doing this requires an API key, which you can get here:
        # https://openweathermap.org/api

        requestUrl = "https://api.openweathermap.org/data/2.5/onecall?appid={}&lat={}&lon={}&exclude=minutely,hourly&units=metric".format(
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

        airQuality = None
        if utils.isValidStr(self.__iqAirApiKey):
            airQuality = self.__fetchAirQuality(location)

        return WeatherReport(
            airQuality = airQuality,
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

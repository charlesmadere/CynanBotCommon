from abc import ABC, abstractmethod

try:
    from CynanBotCommon.location.location import Location
    from CynanBotCommon.weather.weatherReport import WeatherReport
except:
    from location.location import Location
    from weather.weatherReport import WeatherReport


class WeatherRepositoryInterface(ABC):

    @abstractmethod
    async def clearCaches(self):
        pass

    @abstractmethod
    async def fetchWeather(self, location: Location) -> WeatherReport:
        pass

from abc import abstractmethod

try:
    from CynanBotCommon.clearable import Clearable
    from CynanBotCommon.location.location import Location
    from CynanBotCommon.weather.weatherReport import WeatherReport
except:
    from clearable import Clearable
    from location.location import Location
    from weather.weatherReport import WeatherReport


class WeatherRepositoryInterface(Clearable):

    @abstractmethod
    async def fetchWeather(self, location: Location) -> WeatherReport:
        pass

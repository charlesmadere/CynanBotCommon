from datetime import datetime, timedelta
from json.decoder import JSONDecodeError

import requests
from requests import ConnectionError, HTTPError, Timeout
from urllib3.exceptions import MaxRetryError, NewConnectionError

import CynanBotCommon.utils as utils


class JokeResponse():

    def __init__(self, text: str):
        if not utils.isValidStr(text):
            raise ValueError(f'text argument is malformed: \"{text}\"')

        self.__text = text

    def getText(self):
        return self.__text

    def toStr(self):
        return f'{self.__text} 🥁'


class JokesRepository():

    def __init__(
        self,
        apiUrl: str = 'https://v2.jokeapi.dev/joke/Miscellaneous,Pun,Spooky,Christmas?blacklistFlags=nsfw,religious,political,racist,sexist,explicit&safe-mode',
        cacheTimeDelta: timedelta = timedelta(minutes = 10)
    ):
        if not utils.isValidUrl(apiUrl):
            raise ValueError(f'apiUrl argument is malformed: \"{apiUrl}\"')
        elif cacheTimeDelta is None:
            raise ValueError(f'cacheTimeDelta argument is malformed: \"{cacheTimeDelta}\"')

        self.__apiUrl = apiUrl
        self.__cacheTime = datetime.now() - cacheTimeDelta
        self.__cacheTimeDelta = cacheTimeDelta
        self.__jokeResponse = None

    def fetchJoke(self) -> JokeResponse:
        if self.__cacheTime + self.__cacheTimeDelta < datetime.now() or self.__jokeResponse is None:
            self.__jokeResponse = self.__refreshJoke()
            self.__cacheTime = datetime.now()

        return self.__jokeResponse

    def __refreshJoke(self) -> JokeResponse:
        print(f'Refreshing joke... ({utils.getNowTimeText()})')

        rawResponse = None

        try:
            rawResponse = requests.get(url = self.__apiUrl, timeout = utils.getDefaultTimeout())
        except (ConnectionError, HTTPError, MaxRetryError, NewConnectionError, Timeout) as e:
            print(f'Exception occurred when attempting to fetch new joke: {e}')
            raise RuntimeError(f'Exception occurred when attempting to fetch new joke: {e}')

        jsonResponse = None
        try:
            jsonResponse = rawResponse.json()
        except JSONDecodeError as e:
            print(f'Exception occurred when attempting to decode joke\'s response into JSON: {e}')
            raise RuntimeError(f'Exception occurred when attempting to decode joke\'s response into JSON: {e}')

        if utils.getBoolFromDict(jsonResponse, 'error', True):
            print(f'Rejecting joke due to bad \"error\" value: {jsonResponse}')
            raise ValueError(f'Rejecting joke due to bad \"error\" value: {jsonResponse}')
        elif utils.getBoolFromDict(jsonResponse, 'safe', False):
            print(f'Rejecting joke due to bad \"safe\" value: {jsonResponse}')
            raise ValueError(f'Rejecting joke due to bad \"safe\" value: {jsonResponse}')

        flagsJson = jsonResponse['flags']
        isExplicit = flagsJson['explicit']
        isNsfw = flagsJson['nsfw']
        isPolitical = flagsJson['political']
        isRacist = flagsJson['racist']
        isReligious = flagsJson['religious']
        isSexist = flagsJson['sexist']

        if isExplicit or isNsfw or isPolitical or isRacist or isReligious or isSexist:
            print(f'Rejecting joke due to one or more bad flags: {jsonResponse}')
            raise ValueError(f'Rejecting joke due to one or more bad flags: {jsonResponse}')

        jokeText = None

        if jsonResponse['type'] == 'twopart':
            setup = utils.cleanStr(jsonResponse['setup'])
            delivery = utils.cleanStr(jsonResponse['delivery'])
            jokeText = f'{setup} {delivery}'
        elif jsonResponse['type'] == 'single':
            jokeText = utils.cleanStr(jsonResponse['joke'])
        else:
            print(f'Rejecting joke due to unknown \"type\": {jsonResponse}')
            raise ValueError(f'Rejecting joke due to unknown \"type\": {jsonResponse}')

        return JokeResponse(
            text = jokeText
        )

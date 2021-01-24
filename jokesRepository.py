import json
from datetime import datetime, timedelta

import requests
from requests import ConnectionError, HTTPError, Timeout
from urllib3.exceptions import MaxRetryError, NewConnectionError

import CynanBotCommon.utils as utils


class JokesRepository():

    def __init__(
        self,
        apiUrl: str = 'https://v2.jokeapi.dev/joke/Miscellaneous,Pun,Spooky,Christmas?blacklistFlags=nsfw,religious,political,racist,sexist,explicit',
        cacheTimeDelta: timedelta = timedelta(minutes=10)
    ):
        if not utils.isValidUrl(apiUrl):
            raise ValueError(f'apiUrl argument is malformed: \"{apiUrl}\"')
        elif cacheTimeDelta is None:
            raise ValueError(f'cacheTimeDelta argument is malformed: \"{cacheTimeDelta}\"')

        self.__apiUrl = apiUrl
        self.__cacheTime = datetime.now() - cacheTimeDelta
        self.__cacheTimeDelta = cacheTimeDelta
        self.__jokeResponse = None

    def fetchJoke(self):
        if self.__cacheTime + self.__cacheTimeDelta < datetime.now() or self.__jokeResponse is None:
            self.__jokeResponse = self.__refreshJoke()
            self.__cacheTime = datetime.now()

        return self.__jokeResponse

    def __refreshJoke(self):
        print(f'Refreshing joke... ({utils.getNowTimeText()})')

        rawResponse = None

        try:
            rawResponse = requests.get(url=self.__apiUrl, timeout=utils.getDefaultTimeout())
        except (ConnectionError, HTTPError, MaxRetryError, NewConnectionError, Timeout) as e:
            print(f'Exception occurred when attempting to fetch new joke: {e}')

        if rawResponse is None:
            print(f'rawResponse is malformed: \"{rawResponse}\"')
            return None

        jsonResponse = rawResponse.json()

        if jsonResponse['error']:
            print(f'Rejecting joke due to bad \"error\" value: \"{jsonResponse}\"')
            return None

        if not jsonResponse['safe']:
            print(f'Rejecting joke due to bad \"safe\" value: \"{jsonResponse}\"')
            return None

        flagsJson = jsonResponse['flags']
        isExplicit = flagsJson['explicit']
        isNsfw = flagsJson['nsfw']
        isPolitical = flagsJson['political']
        isRacist = flagsJson['racist']
        isReligious = flagsJson['religious']
        isSexist = flagsJson['sexist']

        if isExplicit or isNsfw or isPolitical or isRacist or isReligious or isSexist:
            print(f'Rejecting joke due to one or more bad flags: {jsonResponse}')
            return None

        jokeText = None

        if jsonResponse['type'] == 'twopart':
            setup = utils.cleanStr(jsonResponse['setup'])
            delivery = utils.cleanStr(jsonResponse['delivery'])
            jokeText = f'{setup} {delivery}'
        elif jsonResponse['type'] == 'single':
            jokeText = utils.cleanStr(jsonResponse['joke'])
        else:
            print(f'Rejecting joke due to unknown type: {jsonResponse}')
            return None

        jokeResponse = None

        try:
            jokeResponse = JokeResponse(
                text=jokeText
            )
        except ValueError:
            print(f'Joke has a data error: \"{jsonResponse}\"')

        return jokeResponse


class JokeResponse():

    def __init__(self, text: str):
        if not utils.isValidStr(text):
            raise ValueError(f'text argument is malformed: \"{text}\"')

        self.__text = text

    def getText(self):
        return self.__text

    def toStr(self):
        return f'{self.__text} 🥁'

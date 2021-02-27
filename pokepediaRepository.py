from enum import Enum, auto
from json.decoder import JSONDecodeError
from typing import Dict, List

import requests
from requests import ConnectionError, HTTPError, Timeout
from urllib3.exceptions import MaxRetryError, NewConnectionError

import CynanBotCommon.utils as utils


class PokepediaGeneration(Enum):
    GENERATION_1 = auto()
    GENERATION_2 = auto()
    GENERATION_3 = auto()
    GENERATION_4 = auto()
    GENERATION_5 = auto()
    GENERATION_6 = auto()
    GENERATION_7 = auto()
    GENERATION_8 = auto()

    @classmethod
    def fromStr(cls, text: str):
        if not utils.isValidStr(text):
            raise ValueError(f'text argument is malformed: \"{text}\"')

        if text == 'gold-silver' or text == 'crystal':
            return cls.GENERATION_2
        elif text == 'ruby-sapphire' or text == 'emerald' or text == 'firered-leafgreen':
            return cls.GENERATION_3
        elif text == 'diamond-pearl' or text == 'platinum' or text == 'heartgold-soulsilver':
            return cls.GENERATION_4
        elif text == 'black-white' or text == 'black-2-white-2':
            return cls.GENERATION_5
        elif text == 'x-y' or text == 'omega-ruby-alpha-sapphire':
            return cls.GENERATION_6
        elif text == 'sun-moon' or text == 'ultra-sun-ultra-moon':
            return cls.GENERATION_7

        raise ValueError(f'text argument pertains to unknown generation: \"{text}\"')


class PokepediaMove():

    def __init__(
        self,
        name: str,
        rawName: str
    ):
        if not utils.isValidStr(name):
            raise ValueError(f'name argument is malformed: \"{name}\"')
        elif not utils.isValidStr(rawName):
            raise ValueError(f'rawName argument is malformed: \"{rawName}\"')

        self.__name = name
        self.__rawName = rawName

    def getName(self) -> str:
        return self.__name

    def getRawName(self) -> str:
        return self.__rawName


class PokepediaRepository():

    def __init__(self):
        pass

    def __getEnName(jsonResponse: Dict) -> str:
        if jsonResponse is None:
            raise ValueError(f'jsonResponse argument is malformed: \"{jsonResponse}\"')

        names = jsonResponse['names']
        if not utils.hasItems(names):
            raise ValueError(f'\"names\" field in JSON response is empty: {jsonResponse}')

        for name in names:
            if name['language']['name'] == 'en':
                return name['name']

        raise RuntimeError(f'can\'t find \"en\" language name in \"names\" field: {names}')

    def searchMoves(self, name: str):
        if not utils.isValidStr(name):
            raise ValueError(f'name argument is malformed: \"{name}\"')

        name = utils.cleanStr(name)
        name = name.replace(' ', '-')

        rawResponse = None
        try:
            rawResponse = requests.get(
                url = f'https://pokeapi.co/api/v2/move/{name}/',
                timeout = utils.getDefaultTimeout()
            )
        except (ConnectionError, HTTPError, MaxRetryError, NewConnectionError, Timeout) as e:
            print(f'Exception occurred when attempting to fetch Pokemon move \"{name}\": {e}')
            raise RuntimeError(f'Exception occurred when attempting to fetch Pokemon move \"{name}\": {e}')

        jsonResponse = None
        try:
            jsonResponse = rawResponse.json()
        except JSONDecodeError as e:
            print(f'Exception occurred when attempting to decode Pokemon move response into JSON for \"{name}\": {e}')
            raise RuntimeError(f'Exception occurred when attempting to decode Pokemon move response into JSON for \"{name}\": {e}')

        return PokepediaMove(
            name = self.__getEnName(jsonResponse),
            rawName = jsonResponse['name']
        )

    def searchPokemon(self, name: str):
        if not utils.isValidStr(name):
            raise ValueError(f'name argument is malformed: \"{name}\"')

        # TODO

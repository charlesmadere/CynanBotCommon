import locale
from enum import Enum, auto
from json.decoder import JSONDecodeError
from typing import Dict, List

import requests
from requests import ConnectionError, HTTPError, Timeout
from urllib3.exceptions import MaxRetryError, NewConnectionError

# import CynanBotCommon.utils as utils
import utils

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

        if text == 'gold-silver' or text == 'crystal' or text == 'generation-ii':
            return cls.GENERATION_2
        elif text == 'ruby-sapphire' or text == 'emerald' or text == 'firered-leafgreen' or text == 'generation-iii':
            return cls.GENERATION_3
        elif text == 'diamond-pearl' or text == 'platinum' or text == 'heartgold-soulsilver' or text == 'generation-iv':
            return cls.GENERATION_4
        elif text == 'black-white' or text == 'black-2-white-2' or text == 'generation-v':
            return cls.GENERATION_5
        elif text == 'x-y' or text == 'omega-ruby-alpha-sapphire' or text == 'generation-vi':
            return cls.GENERATION_6
        elif text == 'sun-moon' or text == 'ultra-sun-ultra-moon' or text == 'generation-vii':
            return cls.GENERATION_7
        elif text == 'sword-shield' or text == 'brilliant-diamond-shining-pearl' or text == 'generation-viii':
            return cls.GENERATION_8
        else:
            return cls.GENERATION_1


class PokepediaType(Enum):

    BUG = auto()
    DARK = auto()
    DRAGON = auto()
    ELECTRIC = auto()
    FAIRY = auto()
    FIGHTING = auto()
    FIRE = auto()
    FLYING = auto()
    GHOST = auto()
    GRASS = auto()
    GROUND = auto()
    ICE = auto()
    NORMAL = auto()
    POISON = auto()
    PSYCHIC = auto()
    ROCK = auto()
    STEEL = auto()
    WATER = auto()


class PokepediaMoveType(Enum):

    NORMAL = auto()
    SPECIAL = auto()


class PokepediaMoveGeneration():

    def __init__(
        self,
        accuracy: float,
        power: int,
        pp: int,
        moveType: PokepediaMoveType,
        pokepediaType: PokepediaType
    ):
        if not utils.isValidNum(accuracy):
            raise ValueError(f'accuracy argument is malformed: \"{accuracy}\"')
        elif not utils.isValidNum(power):
            raise ValueError(f'power argument is malformed: \"{power}\"')
        elif not utils.isValidNum(pp):
            raise ValueError(f'pp argument is malformed: \"{pp}\"')
        elif moveType is None:
            raise ValueError(f'moveType argument is malformed: \"{moveType}\"')
        elif pokepediaType is None:
            raise ValueError(f'pokepediaType argument is malformed: \"{pokepediaType}\"')

        self.__accuracy = accuracy
        self.__power = power
        self.__pp = pp
        self.__moveType = moveType
        self.__pokepediaType = pokepediaType

    def getAccuracy(self) -> float:
        return self.__accuracy

    def getMoveType(self) -> PokepediaMoveType:
        return self.__moveType

    def getPower(self) -> int:
        return self.__power

    def getPp(self) -> int:
        return self.__pp

    def getType(self) -> PokepediaType:
        return self.__pokepediaType


class PokepediaMove():

    def __init__(
        self,
        # pokepediaType: PokepediaType,
        name: str,
        rawName: str,
        genDictionary: Dict[PokepediaGeneration, PokepediaMoveGeneration]
    ):
        '''
        if pokepediaType is None:
            raise ValueError(f'pokepediaType argument is malformed: \"{pokepediaType}\"')
        elif not utils.isValidStr(name):
            raise ValueError(f'name argument is malformed: \"{name}\"')
        elif not utils.isValidStr(rawName):
            raise ValueError(f'rawName argument is malformed: \"{rawName}\"')
        '''

        # self.__pokepediaType = pokepediaType
        self.__name = name
        self.__rawName = rawName
        self.__genDictionary = genDictionary

    def getName(self) -> str:
        return self.__name

    def getRawName(self) -> str:
        return self.__rawName

    def getGenDictionary(self) -> Dict[PokepediaGeneration, PokepediaMoveGeneration]:
        return self.__genDictionary

class PokepediaPokemon():

    def __init__(
        self,
        pokedexId: int,
        pokepediaTypes: Dict[PokepediaGeneration, PokepediaType],
        name: str
    ):
        if not utils.isValidNum(pokedexId):
            raise ValueError(f'pokedexId argument is malformed: \"{pokedexId}\"')
        if not utils.hasItems(pokepediaTypes):
            raise ValueError(f'pokepediaTypes argument is malformed: \"{pokepediaTypes}\"')
        elif not utils.isValidStr(name):
            raise ValueError(f'name argument is malformed: \"{name}\"')

        self.__pokedexId = pokedexId
        self.__pokepediaTypes = pokepediaTypes
        self.__name = name

    def getName(self) -> str:
        return self.__name

    def getPokedexId(self) -> int:
        return self.__pokedexId

    def getPokedexIdStr(self) -> str:
        return locale.format_string("%d", self.__pokedexId, grouping = True)

    def getPokepediaTypes(self) -> List[PokepediaType]:
        return self.__pokepediaTypes


class PokepediaRepository():

    def __init__(self):
        pass

    def __getEnName(self, jsonResponse: Dict) -> str:
        if jsonResponse is None:
            raise ValueError(f'jsonResponse argument is malformed: \"{jsonResponse}\"')

        names = jsonResponse['names']
        if not utils.hasItems(names):
            raise ValueError(f'\"names\" field in JSON response is empty: {jsonResponse}')

        for name in names:
            if name['language']['name'] == 'en':
                return name['name'].capitalize()

        raise RuntimeError(f'can\'t find \"en\" language name in \"names\" field: {names}')

    def __getPokepediaMoveDictionary(self, jsonResponse: Dict) -> Dict[PokepediaGeneration, PokepediaMoveGeneration]:
        if jsonResponse is None:
            raise ValueError(f'jsonResponse argument is malformed: \"{jsonResponse}\"')

        generation = jsonResponse['generation']['name']
        accuracy = jsonResponse['accuracy']
        power = jsonResponse['power']
        pp = jsonResponse['pp']
        moveType = PokepediaMoveType.NORMAL
        pokepediaType = PokepediaType.FIRE
        past_values = jsonResponse['past_values']
        pokepediaMoveDictionary = {}

        move = PokepediaMoveGeneration(accuracy, power, pp, moveType, pokepediaType)

        pokepediaMoveDictionary[PokepediaGeneration.fromStr(generation)] = move

        # for past_value in past_values:
            # add to dictionary
        
        return pokepediaMoveDictionary

    def searchMoves(self, name: str) -> PokepediaMove:
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
            rawName = jsonResponse['name'],
            genDictionary = self.__getPokepediaMoveDictionary(jsonResponse)
        )

    def searchPokemon(self, name: str) -> PokepediaPokemon:
        if not utils.isValidStr(name):
            raise ValueError(f'name argument is malformed: \"{name}\"')

        name = utils.cleanStr(name)

        rawResponse = None
        try:
            rawResponse = requests.get(
                url = f'https://pokeapi.co/api/v2/pokemon/{name}/',
                timeout = utils.getDefaultTimeout()
            )
        except (ConnectionError, HTTPError, MaxRetryError, NewConnectionError, Timeout) as e:
            print(f'Exception occurred when attempting to fetch Pokemon \"{name}\": {e}')
            raise RuntimeError(f'Exception occurred when attempting to fetch Pokemon \"{name}\": {e}')

        jsonResponse = None
        try:
            jsonResponse = rawResponse.json()
        except JSONDecodeError as e:
            print(f'Exception occurred when attempting to decode Pokemon response into JSON for \"{name}\": {e}')
            raise RuntimeError(f'Exception occurred when attempting to decode Pokemon response into JSON for \"{name}\": {e}')

        return PokepediaPokemon(
            name = jsonResponse['name'].capitalize()
        )

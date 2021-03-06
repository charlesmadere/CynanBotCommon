import locale
from enum import Enum, auto
from json.decoder import JSONDecodeError
from typing import Dict, List

import requests
from requests import ConnectionError, HTTPError, Timeout
from urllib3.exceptions import MaxRetryError, NewConnectionError

import CynanBotCommon.utils as utils
# import utils


class PokepediaElementType(Enum):

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

    @classmethod
    def fromStr(cls, text: str):
        if not utils.isValidStr(text):
            raise ValueError(f'text argument is malformed: \"{text}\"')

        if text == 'bug':
            return cls.BUG
        elif text == 'dark':
            return cls.DARK
        elif text == 'dragon':
            return cls.DRAGON
        elif text == 'electric':
            return cls.ELECTRIC
        elif text == 'fairy':
            return cls.FAIRY
        elif text == 'fighting':
            return cls.FIGHTING
        elif text == 'fire':
            return cls.FIRE
        elif text == 'flying':
            return cls.FLYING
        elif text == 'ghost':
            return cls.GHOST
        elif text == 'grass':
            return cls.GRASS
        elif text == 'ground':
            return cls.GROUND
        elif text == 'ice':
            return cls.ICE
        elif text == 'normal':
            return cls.NORMAL
        elif text == 'poison':
            return cls.POISON
        elif text == 'psychic':
            return cls.PSYCHIC
        elif text == 'rock':
            return cls.ROCK
        elif text == 'steel':
            return cls.STEEL
        elif text == 'water':
            return cls.WATER
        else:
            raise ValueError(f'unknown PokepediaElementType: \"{text}\'')

    def getEmoji(self) -> str:
        if self is PokepediaElementType.BUG:
            return '🐛'
        elif self is PokepediaElementType.DRAGON:
            return '🐲'
        elif self is PokepediaElementType.ELECTRIC:
            return '⚡'
        elif self is PokepediaElementType.FIGHTING:
            return '🥊'
        elif self is PokepediaElementType.FIRE:
            return '🔥'
        elif self is PokepediaElementType.FLYING:
            return '🐦'
        elif self is PokepediaElementType.GRASS:
            return '🍃'
        elif self is PokepediaElementType.GHOST:
            return '👻'
        elif self is PokepediaElementType.ICE:
            return '❄'
        elif self is PokepediaElementType.POISON:
            return '🧪'
        elif self is PokepediaElementType.PSYCHIC:
            return '🧠'
        elif self is PokepediaElementType.WATER:
            return '🌊'
        else:
            return None

    def getEmojiOrStr(self) -> str:
        emoji = self.getEmoji()

        if utils.isValidStr(emoji):
            return emoji
        else:
            return self.toStr()

    def toStr(self) -> str:
        if self is PokepediaElementType.BUG:
            return 'Bug'
        elif self is PokepediaElementType.DARK:
            return 'Dark'
        elif self is PokepediaElementType.DRAGON:
            return 'Dragon'
        elif self is PokepediaElementType.ELECTRIC:
            return 'Electric'
        elif self is PokepediaElementType.FAIRY:
            return 'Fairy'
        elif self is PokepediaElementType.FIGHTING:
            return 'Fighting'
        elif self is PokepediaElementType.FIRE:
            return 'Fire'
        elif self is PokepediaElementType.FLYING:
            return 'Flying'
        elif self is PokepediaElementType.GHOST:
            return 'Ghost'
        elif self is PokepediaElementType.GRASS:
            return 'Grass'
        elif self is PokepediaElementType.GROUND:
            return 'Ground'
        elif self is PokepediaElementType.ICE:
            return 'Ice'
        elif self is PokepediaElementType.NORMAL:
            return 'Normal'
        elif self is PokepediaElementType.POISON:
            return 'Poison'
        elif self is PokepediaElementType.PSYCHIC:
            return 'Psychic'
        elif self is PokepediaElementType.ROCK:
            return 'Rock'
        elif self is PokepediaElementType.STEEL:
            return 'Steel'
        elif self is PokepediaElementType.WATER:
            return 'Water'
        else:
            raise RuntimeError(f'unknown PokepediaElementType: \"{self}\"')


class PokepediaDamageClass(Enum):

    PHYSICAL = auto()
    SPECIAL = auto()
    STATUS = auto()

    @classmethod
    def fromStr(cls, text: str):
        if not utils.isValidStr(text):
            raise ValueError(f'text argument is malformed: \"{text}\"')

        if text == 'physical':
            return cls.PHYSICAL
        elif text == 'special':
            return cls.SPECIAL
        elif text == 'status':
            return cls.STATUS
        else:
            raise ValueError(f'unknown PokepediaDamageClass: \"{text}\"')

    def toStr(self) -> str:
        if self is PokepediaDamageClass.PHYSICAL:
            return 'Physical'
        elif self is PokepediaDamageClass.SPECIAL:
            return 'Special'
        elif self is PokepediaDamageClass.STATUS:
            return 'Status'
        else:
            raise RuntimeError(f'unknown PokepediaDamageClass: \"{self}\"')

    # gen 1-3 have damage classes based off element type
    @classmethod
    def getTypeBasedClass(cls, element: PokepediaElementType):
        physicalList = [PokepediaElementType.NORMAL,PokepediaElementType.FIGHTING,PokepediaElementType.FLYING,PokepediaElementType.POISON,PokepediaElementType.GROUND,PokepediaElementType.ROCK,PokepediaElementType.BUG,PokepediaElementType.GHOST,PokepediaElementType.STEEL]
        specialList = [PokepediaElementType.FIRE,PokepediaElementType.WATER,PokepediaElementType.GRASS,PokepediaElementType.ELECTRIC,PokepediaElementType.PSYCHIC,PokepediaElementType.ICE,PokepediaElementType.DRAGON,PokepediaElementType.DARK]

        if element in physicalList:
            return cls.PHYSICAL
        elif element in specialList:
            return cls.SPECIAL
        else:
            raise ValueError(f'unknown PokepediaElementType: \"{element}\"')


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

    def toStr(self) -> str:
        if self is PokepediaGeneration.GENERATION_1:
            return 'G1'
        elif self is PokepediaGeneration.GENERATION_2:
            return 'G2'
        elif self is PokepediaGeneration.GENERATION_3:
            return 'G3'
        elif self is PokepediaGeneration.GENERATION_4:
            return 'G4'
        elif self is PokepediaGeneration.GENERATION_5:
            return 'G5'
        elif self is PokepediaGeneration.GENERATION_6:
            return 'G6'
        elif self is PokepediaGeneration.GENERATION_7:
            return 'G7'
        elif self is PokepediaGeneration.GENERATION_8:
            return 'G8'
        else:
            raise RuntimeError(f'unknown PokepediaGeneration: \"{self}\"')


class PokepediaMoveGeneration():

    def __init__(
        self,
        accuracy: int,
        power: int,
        pp: int,
        damageClass: PokepediaDamageClass,
        elementType: PokepediaElementType,
        generation: PokepediaGeneration
    ):
        if not utils.isValidNum(pp):
            raise ValueError(f'pp argument is malformed: \"{pp}\"')
        elif damageClass is None:
            raise ValueError(f'damageClass argument is malformed: \"{damageClass}\"')
        elif elementType is None:
            raise ValueError(f'elementType argument is malformed: \"{elementType}\"')
        elif generation is None:
            raise ValueError(f'generation argument is malformed: \"{generation}\"')

        self.__accuracy = accuracy
        self.__power = power
        self.__pp = pp
        self.__damageClass = damageClass
        self.__elementType = elementType
        self.__generation = generation

    def getAccuracy(self) -> int:
        return self.__accuracy

    def getAccuracyStr(self) -> str:
        formattedAccuracy = locale.format_string("%d", self.__accuracy, grouping = True)
        return f'{formattedAccuracy}%'

    def getDamageClass(self) -> PokepediaDamageClass:
        return self.__damageClass

    def getElementType(self) -> PokepediaElementType:
        return self.__elementType

    def getGeneration(self) -> PokepediaGeneration:
        return self.__generation

    def getPower(self) -> int:
        if self.hasPower():
            return self.__power
        else:
            return RuntimeError(f'This PokepediaGenerationMove does not have a power value!')

    def getPowerStr(self) -> str:
        if self.hasPower():
            return locale.format_string("%d", self.__power, grouping = True)
        else:
            return None

    def getPp(self) -> int:
        return self.__pp

    def getPpStr(self) -> str:
        formattedPp = locale.format_string("%d", self.__pp, grouping = True)
        return f'{formattedPp}pp'

    def hasPower(self) -> bool:
        return utils.isValidNum(self.__power)

    def hasAccuracy(self) -> bool:
        return utils.isValidNum(self.__accuracy)

    def toStr(self) -> str:
        powerStr = ''
        accuracyStr = ''
        if self.hasPower():
            powerStr = f'💪 {self.getPowerStr()}, '
        if self.hasAccuracy():
            accuracyStr = f'🎯 {self.getAccuracyStr()}, '
        return f'{self.__generation.toStr()}: {powerStr}{accuracyStr}{self.getPpStr()}, {self.__elementType.getEmojiOrStr().lower()} type, {self.__damageClass.toStr().lower()}'


class PokepediaMove():

    def __init__(
        self,
        generationMoves: Dict[PokepediaGeneration, PokepediaMoveGeneration],
        description: str,
        name: str,
        rawName: str
    ):
        if not utils.hasItems(generationMoves):
            raise ValueError(f'generationMoves argument is malformed: \"{generationMoves}\"')
        elif not utils.isValidStr(description):
            raise ValueError(f'description argument is malformed: \"{description}\"')
        elif not utils.isValidStr(name):
            raise ValueError(f'name argument is malformed: \"{name}\"')
        elif not utils.isValidStr(rawName):
            raise ValueError(f'rawName argument is malformed: \"{rawName}\"')

        self.__generationMoves = generationMoves
        self.__description = description
        self.__name = name
        self.__rawName = rawName

    def getGenerationMoves(self) -> Dict[PokepediaGeneration, PokepediaMoveGeneration]:
        return self.__generationMoves

    def getName(self) -> str:
        return self.__name

    def getRawName(self) -> str:
        return self.__rawName

    def getDescription(self) -> str:
        return self.__description

    def toStr(self, delimiter: str = '; ') -> str:
        if delimiter is None:
            raise ValueError(f'delimiter argument is malformed: \"{delimiter}\"')

        genMoveStrings = list()

        for gen in PokepediaGeneration:
            if gen in self.__generationMoves:
                genMove = self.__generationMoves[gen]
                genMoveStrings.append(genMove.toStr())

        genMoveString = delimiter.join(genMoveStrings)
        return f'{self.getName()} — {genMoveString}'
    
    def toStrList(self) -> List[str]:
        genMoveStrings = list()
        genMoveStrings.append(f'{self.getName()} — {self.getDescription()}')

        for gen in PokepediaGeneration:
            if gen in self.__generationMoves:
                genMove = self.__generationMoves[gen]
                genMoveStrings.append(genMove.toStr())

        return genMoveStrings


class PokepediaPokemon():

    def __init__(
        self,
        generationElementTypes: Dict[PokepediaGeneration, PokepediaElementType],
        pokedexId: int,
        name: str
    ):
        if not utils.hasItems(generationElementTypes):
            raise ValueError(f'generationElementTypes argument is malformed: \"{generationElementTypes}\"')
        elif not utils.isValidNum(pokedexId):
            raise ValueError(f'pokedexId argument is malformed: \"{pokedexId}\"')
        elif not utils.isValidStr(name):
            raise ValueError(f'name argument is malformed: \"{name}\"')

        self.__generationElementTypes = generationElementTypes
        self.__pokedexId = pokedexId
        self.__name = name

    def getGenerationElementTypes(self) -> Dict[PokepediaGeneration, PokepediaElementType]:
        return self.__generationElementTypes

    def getName(self) -> str:
        return self.__name

    def getPokedexId(self) -> int:
        return self.__pokedexId

    def getPokedexIdStr(self) -> str:
        return locale.format_string("%d", self.__pokedexId, grouping = True)


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
                return utils.cleanStr(name['name'].title())

        raise RuntimeError(f'can\'t find \"en\" language name in \"names\" field: {names}')

    def __getPokepediaMoveDictionary(self, jsonResponse: Dict) -> Dict[PokepediaGeneration, PokepediaMoveGeneration]:
        if jsonResponse is None:
            raise ValueError(f'jsonResponse argument is malformed: \"{jsonResponse}\"')

        pokepediaMoveDictionary = {}

        # begin with current gen stats
        accuracy = jsonResponse['accuracy']
        power = jsonResponse['power']
        pp = jsonResponse['pp']
        damageClass = PokepediaDamageClass.fromStr(jsonResponse['damage_class']['name'])
        elementType = PokepediaElementType.fromStr(jsonResponse['type']['name'])
        move = None
        #

        past_values = jsonResponse['past_values']

        # iterate backwards and insert to dictionary once a gen is found. then 'un-patch' for previous gens
        for past_value in reversed(past_values):
            generation = PokepediaGeneration.fromStr(past_value['version_group']['name'])

            if damageClass is not PokepediaDamageClass.STATUS and generation is PokepediaGeneration.GENERATION_1 or generation is PokepediaGeneration.GENERATION_2 or generation is PokepediaGeneration.GENERATION_3:
                damageClass = PokepediaDamageClass.getTypeBasedClass(elementType)

            move = PokepediaMoveGeneration(
                accuracy = accuracy,
                power = power,
                pp = pp,
                damageClass = damageClass,
                elementType = elementType,
                generation = generation
            )

            pokepediaMoveDictionary[generation] = move
            if past_value['accuracy'] is not None:
                accuracy = past_value['accuracy']
            if past_value['power'] is not None:
                power = past_value['power']
            if past_value['pp'] is not None:
                pp = past_value['pp']
            if past_value['type'] is not None:
                elementType = PokepediaElementType.fromStr(past_value['type']['name'])

        generation = PokepediaGeneration.fromStr(jsonResponse['generation']['name'])

        if damageClass is not PokepediaDamageClass.STATUS and generation is PokepediaGeneration.GENERATION_1 or generation is PokepediaGeneration.GENERATION_2 or generation is PokepediaGeneration.GENERATION_3:
            damageClass = PokepediaDamageClass.getTypeBasedClass(elementType)

        move = PokepediaMoveGeneration(
            accuracy = accuracy,
            power = power,
            pp = pp,
            damageClass = damageClass,
            elementType = elementType,
            generation = generation
        )

        pokepediaMoveDictionary[generation] = move

        # TODO scan for case where gen4+ type changed but not reflected in past values
        if PokepediaGeneration.GENERATION_4 not in pokepediaMoveDictionary:
            if PokepediaGeneration.GENERATION_3 in pokepediaMoveDictionary:
                if pokepediaMoveDictionary[PokepediaGeneration.GENERATION_3].getDamageClass() is not PokepediaDamageClass.fromStr(jsonResponse['damage_class']['name']):
                    move = PokepediaMoveGeneration(
                        accuracy = pokepediaMoveDictionary[PokepediaGeneration.GENERATION_3].getAccuracy(),
                        power = pokepediaMoveDictionary[PokepediaGeneration.GENERATION_3].getPower(),
                        pp = pokepediaMoveDictionary[PokepediaGeneration.GENERATION_3].getPp(),
                        damageClass = PokepediaDamageClass.fromStr(jsonResponse['damage_class']['name']),
                        elementType = pokepediaMoveDictionary[PokepediaGeneration.GENERATION_3].getElementType(),
                        generation = PokepediaGeneration.GENERATION_4
                    )
                    pokepediaMoveDictionary[PokepediaGeneration.GENERATION_4] = move
            elif PokepediaGeneration.GENERATION_2 in pokepediaMoveDictionary:
                if pokepediaMoveDictionary[PokepediaGeneration.GENERATION_2].getDamageClass() is not PokepediaDamageClass.fromStr(jsonResponse['damage_class']['name']):
                    move = PokepediaMoveGeneration(
                        accuracy = pokepediaMoveDictionary[PokepediaGeneration.GENERATION_2].getAccuracy(),
                        power = pokepediaMoveDictionary[PokepediaGeneration.GENERATION_2].getPower(),
                        pp = pokepediaMoveDictionary[PokepediaGeneration.GENERATION_2].getPp(),
                        damageClass = PokepediaDamageClass.fromStr(jsonResponse['damage_class']['name']),
                        elementType = pokepediaMoveDictionary[PokepediaGeneration.GENERATION_2].getElementType(),
                        generation = PokepediaGeneration.GENERATION_4
                    )
                    pokepediaMoveDictionary[PokepediaGeneration.GENERATION_4] = move
            elif PokepediaGeneration.GENERATION_1 in pokepediaMoveDictionary:
                if pokepediaMoveDictionary[PokepediaGeneration.GENERATION_1].getDamageClass() is not PokepediaDamageClass.fromStr(jsonResponse['damage_class']['name']):
                    move = PokepediaMoveGeneration(
                        accuracy = pokepediaMoveDictionary[PokepediaGeneration.GENERATION_1].getAccuracy(),
                        power = pokepediaMoveDictionary[PokepediaGeneration.GENERATION_1].getPower(),
                        pp = pokepediaMoveDictionary[PokepediaGeneration.GENERATION_1].getPp(),
                        damageClass = PokepediaDamageClass.fromStr(jsonResponse['damage_class']['name']),
                        elementType = pokepediaMoveDictionary[PokepediaGeneration.GENERATION_1].getElementType(),
                        generation = PokepediaGeneration.GENERATION_4
                    )
                    pokepediaMoveDictionary[PokepediaGeneration.GENERATION_4] = move

        return pokepediaMoveDictionary

    def searchMoves(self, name: str) -> PokepediaMove:
        if not utils.isValidStr(name):
            raise ValueError(f'name argument is malformed: \"{name}\"')

        name = utils.cleanStr(name)
        name = name.replace(' ', '-')
        print(f'Searching for Pokemon move \"{name}\"...')

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

        description = ''
        flavor_text_entries = jsonResponse.get('flavor_text_entries')
        if not utils.hasItems(flavor_text_entries):
            raise ValueError(f'\"flavor_text_entries\" field in JSON response is empty: {jsonResponse}')

        for flavor_text_entry in flavor_text_entries:
            if flavor_text_entry['language']['name'] == 'en':
                description = utils.cleanStr(flavor_text_entry['flavor_text'])
                break

        return PokepediaMove(
            generationMoves = self.__getPokepediaMoveDictionary(jsonResponse),
            description = description,
            name = self.__getEnName(jsonResponse),
            rawName = jsonResponse['name']
        )

    def searchPokemon(self, name: str) -> PokepediaPokemon:
        if not utils.isValidStr(name):
            raise ValueError(f'name argument is malformed: \"{name}\"')

        name = utils.cleanStr(name)
        name = name.replace(' ', '-')
        print(f'Searching for Pokemon \"{name}\"...')

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

        # TODO
        return PokepediaPokemon(
            name = jsonResponse['name'].title()
        )

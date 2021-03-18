import locale
from enum import Enum, auto
from json.decoder import JSONDecodeError
from typing import Dict, List

import requests
from requests import ConnectionError, HTTPError, Timeout
from urllib3.exceptions import MaxRetryError, NewConnectionError

try:
    import CynanBotCommon.utils as utils
except:
    import utils


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
            raise ValueError(f'unknown PokepediaElementType: \"{text}\"')

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
        elif self is PokepediaElementType.GHOST:
            return '👻'
        elif self is PokepediaElementType.GRASS:
            return '🍃'
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

    # gen 1-3 have damage classes based off element type
    @classmethod
    def getTypeBasedDamageClass(cls, elementType: PokepediaElementType):
        if elementType is None:
            raise ValueError(f'elementType argument is malformed: \"{elementType}\"')

        physicalElementTypes = [ PokepediaElementType.BUG, PokepediaElementType.FIGHTING, PokepediaElementType.FLYING, PokepediaElementType.GHOST, PokepediaElementType.GROUND, PokepediaElementType.NORMAL, PokepediaElementType.POISON, PokepediaElementType.ROCK, PokepediaElementType.STEEL ]
        specialElementTypes = [ PokepediaElementType.DARK, PokepediaElementType.DRAGON, PokepediaElementType.ELECTRIC, PokepediaElementType.FIRE, PokepediaElementType.GRASS, PokepediaElementType.ICE, PokepediaElementType.PSYCHIC, PokepediaElementType.WATER ]

        if elementType in physicalElementTypes:
            return cls.PHYSICAL
        elif elementType in specialElementTypes:
            return cls.SPECIAL
        else:
            raise ValueError(f'unknown PokepediaElementType: \"{elementType}\"')

    def toStr(self) -> str:
        if self is PokepediaDamageClass.PHYSICAL:
            return 'Physical'
        elif self is PokepediaDamageClass.SPECIAL:
            return 'Special'
        elif self is PokepediaDamageClass.STATUS:
            return 'Status'
        else:
            raise RuntimeError(f'unknown PokepediaDamageClass: \"{self}\"')


class PokepediaDamageMultiplier(Enum):

    ZERO = auto()
    ZERO_POINT_TWO_FIVE = auto()
    ZERO_POINT_FIVE = auto()
    ONE = auto()
    TWO = auto()
    FOUR = auto()

    def multiply(self, other):
        if other is None:
            raise ValueError(f'other argument is malformed: \"{other}\"')
        elif other is PokepediaDamageMultiplier.ZERO_POINT_TWO_FIVE or other is PokepediaDamageMultiplier.FOUR:
            raise RuntimeError(f'We should never be multiplying this PokepediaDamageMultiplier ({self}) by anything else ({other} in this case)')

        if self is PokepediaDamageMultiplier.ZERO:
            return PokepediaDamageMultiplier.ZERO
        elif self is PokepediaDamageMultiplier.ZERO_POINT_TWO_FIVE:
            raise RuntimeError(f'We should never be multiplying this PokepediaDamageMultiplier ({self}) by anything else ({other} in this case)')
        elif self is PokepediaDamageMultiplier.ZERO_POINT_FIVE:
            if other is PokepediaDamageMultiplier.ZERO:
                return PokepediaDamageMultiplier.ZERO
            elif other is PokepediaDamageMultiplier.ZERO_POINT_FIVE:
                return PokepediaDamageMultiplier.ZERO_POINT_TWO_FIVE
            elif other is PokepediaDamageMultiplier.TWO:
                return PokepediaDamageMultiplier.ONE
        elif self is PokepediaDamageMultiplier.ONE:
            return other
        elif self is PokepediaDamageMultiplier.TWO:
            if other is PokepediaDamageMultiplier.ZERO:
                return PokepediaDamageMultiplier.ZERO
            elif other is PokepediaDamageMultiplier.ZERO_POINT_FIVE:
                return PokepediaDamageMultiplier.ONE
            elif other is PokepediaDamageMultiplier.TWO:
                return PokepediaDamageMultiplier.FOUR

        raise RuntimeError(f'unknown PokepediaDamageMultiplier: \"{self}\"')

    def toStr(self) -> str:
        if self is PokepediaDamageMultiplier.ZERO:
            return '0x'
        elif self is PokepediaDamageMultiplier.ZERO_POINT_TWO_FIVE:
            return '0.25x'
        elif self is PokepediaDamageMultiplier.ZERO_POINT_FIVE:
            return '0.5x'
        elif self is PokepediaDamageMultiplier.ONE:
            return '1x'
        elif self is PokepediaDamageMultiplier.TWO:
            return '2x'
        elif self is PokepediaDamageMultiplier.FOUR:
            return '4x'
        else:
            raise RuntimeError(f'unknown PokepediaDamageMultiplier: \"{self}\"')


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

    def isEarlyGeneration(self) -> bool:
        return self is PokepediaGeneration.GENERATION_1 or self is PokepediaGeneration.GENERATION_2 or self is PokepediaGeneration.GENERATION_3

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
        if self.hasAccuracy():
            formattedAccuracy = locale.format_string("%d", self.__accuracy, grouping = True)
            return f'{formattedAccuracy}%'
        else:
            raise RuntimeError(f'This PokepediaGenerationMove ({self}) does not have an accuracy value!')

    def getDamageClass(self) -> PokepediaDamageClass:
        return self.__damageClass

    def getElementType(self) -> PokepediaElementType:
        return self.__elementType

    def getGeneration(self) -> PokepediaGeneration:
        return self.__generation

    def getPower(self) -> int:
        return self.__power

    def getPowerStr(self) -> str:
        if self.hasPower():
            return locale.format_string("%d", self.__power, grouping = True)
        else:
            raise RuntimeError(f'This PokepediaGenerationMove ({self}) does not have a power value!')

    def getPp(self) -> int:
        return self.__pp

    def getPpStr(self) -> str:
        formattedPp = locale.format_string("%d", self.__pp, grouping = True)
        return f'{formattedPp}pp'

    def hasAccuracy(self) -> bool:
        return utils.isValidNum(self.__accuracy)

    def hasPower(self) -> bool:
        return utils.isValidNum(self.__power)

    def toStr(self) -> str:
        powerStr = ''
        if self.hasPower():
            powerStr = f'💪 {self.getPowerStr()}, '

        accuracyStr = ''
        if self.hasAccuracy():
            accuracyStr = f'🎯 {self.getAccuracyStr()}, '

        return f'{self.__generation.toStr()}: {powerStr}{accuracyStr}{self.getPpStr()}, {self.__elementType.getEmojiOrStr().lower()} type, {self.__damageClass.toStr().lower()}'


class PokepediaMove():

    def __init__(
        self,
        generationMoves: Dict[PokepediaGeneration, PokepediaMoveGeneration],
        moveId: int,
        description: str,
        name: str,
        rawName: str
    ):
        if not utils.hasItems(generationMoves):
            raise ValueError(f'generationMoves argument is malformed: \"{generationMoves}\"')
        elif not utils.isValidNum(moveId):
            raise ValueError(f'moveId argument is malformed: \"{moveId}\"')
        elif not utils.isValidStr(description):
            raise ValueError(f'description argument is malformed: \"{description}\"')
        elif not utils.isValidStr(name):
            raise ValueError(f'name argument is malformed: \"{name}\"')
        elif not utils.isValidStr(rawName):
            raise ValueError(f'rawName argument is malformed: \"{rawName}\"')

        self.__generationMoves = generationMoves
        self.__moveId = moveId
        self.__description = description
        self.__name = name
        self.__rawName = rawName

    def getDescription(self) -> str:
        return self.__description

    def getGenerationMoves(self) -> Dict[PokepediaGeneration, PokepediaMoveGeneration]:
        return self.__generationMoves

    def getMoveId(self) -> int:
        return self.__moveId

    def getName(self) -> str:
        return self.__name

    def getRawName(self) -> str:
        return self.__rawName

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
        generationElementTypes: Dict[PokepediaGeneration, List[PokepediaElementType]],
        height: int,
        pokedexId: int,
        weight: int,
        name: str
    ):
        if not utils.hasItems(generationElementTypes):
            raise ValueError(f'generationElementTypes argument is malformed: \"{generationElementTypes}\"')
        elif not utils.isValidNum(height):
            raise ValueError(f'height argument is malformed: \"{height}\"')
        elif not utils.isValidNum(pokedexId):
            raise ValueError(f'pokedexId argument is malformed: \"{pokedexId}\"')
        elif not utils.isValidNum(weight):
            raise ValueError(f'weight argument is malformed: \"{weight}\"')
        elif not utils.isValidStr(name):
            raise ValueError(f'name argument is malformed: \"{name}\"')

        self.__generationElementTypes = generationElementTypes
        self.__height = height
        self.__pokedexId = pokedexId
        self.__weight = weight
        self.__name = name

    def getGenerationElementTypes(self) -> Dict[PokepediaGeneration, List[PokepediaElementType]]:
        return self.__generationElementTypes

    def getHeight(self) -> int:
        return self.__height

    def getHeightStr(self) -> str:
        return locale.format_string("%d", self.__height, grouping = True)

    def getName(self) -> str:
        return self.__name

    def getPokedexId(self) -> int:
        return self.__pokedexId

    def getPokedexIdStr(self) -> str:
        return locale.format_string("%d", self.__pokedexId, grouping = True)

    def getWeight(self) -> int:
        return self.__weight

    def getWeightStr(self) -> str:
        return locale.format_string("%d", self.__weight, grouping = True)


class PokepediaTypeChart(Enum):

    GENERATION_1 = auto()
    GENERATION_2_THRU_5 = auto()
    GENERATION_6_AND_ON = auto()

    @classmethod
    def fromPokepediaGeneration(cls, pokepediaGeneration: PokepediaGeneration):
        if pokepediaGeneration is None:
            raise ValueError(f'pokepediaGeneration argument is malformed: \"{pokepediaGeneration}\"')

        if pokepediaGeneration is PokepediaGeneration.GENERATION_1:
            return cls.GENERATION_1
        elif pokepediaGeneration is PokepediaGeneration.GENERATION_2 or pokepediaGeneration is PokepediaGeneration.GENERATION_3 or pokepediaGeneration is PokepediaGeneration.GENERATION_4 or pokepediaGeneration is PokepediaGeneration.GENERATION_5:
            return cls.GENERATION_2_THRU_5
        else:
            return cls.GENERATION_6_AND_ON

    def __getGenerationOneWeaknessesFor(self, types: List[PokepediaElementType]) -> Dict[PokepediaDamageMultiplier, List[PokepediaElementType]]:
        if not utils.hasItems(types):
            raise ValueError(f'types argument is malformed: \"{types}\"')

        weaknesses = dict()

        for elementType in PokepediaElementType:
            weaknesses[elementType] = list()

        for elementType in types:
            if elementType is PokepediaElementType.BUG:
                weaknesses[PokepediaDamageMultiplier.TWO].append(PokepediaElementType.FIRE)
                weaknesses[PokepediaDamageMultiplier.TWO].append(PokepediaElementType.FLYING)
                weaknesses[PokepediaDamageMultiplier.TWO].append(PokepediaElementType.POISON)
                weaknesses[PokepediaDamageMultiplier.TWO].append(PokepediaElementType.ROCK)
            elif elementType is PokepediaElementType.DRAGON:
                weaknesses[PokepediaDamageMultiplier.TWO].append(PokepediaElementType.DRAGON)
                weaknesses[PokepediaDamageMultiplier.TWO].append(PokepediaElementType.ICE)

        raise RuntimeError('Not yet implemented!')

    def __getGenerationTwoThruFiveWeaknessesFor(self, types: List[PokepediaElementType]) -> Dict[PokepediaDamageMultiplier, List[PokepediaElementType]]:
        if not utils.hasItems(types):
            raise ValueError(f'types argument is malformed: \"{types}\"')

        raise RuntimeError('Not yet implemented!')

    def __getGenerationSixAndOnWeaknessesFor(self, types: List[PokepediaElementType]) -> Dict[PokepediaDamageMultiplier, List[PokepediaElementType]]:
        if not utils.hasItems(types):
            raise ValueError(f'types argument is malformed: \"{types}\"')

        raise RuntimeError('Not yet implemented!')

    def getWeaknessesFor(self, types: List[PokepediaElementType]) -> Dict[PokepediaDamageMultiplier, List[PokepediaElementType]]:
        if not utils.hasItems(types):
            raise ValueError(f'types argument is malformed: \"{types}\"')

        if self is PokepediaTypeChart.GENERATION_1:
            return self.__getGenerationOneWeaknessesFor(types)
        elif self is PokepediaTypeChart.GENERATION_2_THRU_5:
            return self.__getGenerationTwoThruFiveWeaknessesFor(types)
        elif self is PokepediaTypeChart.GENERATION_6_AND_ON:
            return self.__getGenerationSixAndOnWeaknessesFor(types)
        else:
            raise RuntimeError(f'unknown PokepediaTypeChart: \"{self}\"')


class PokepediaRepository():

    def __init__(self):
        pass

    def __getElementTypeGenerationDictionary(self, jsonResponse: Dict) -> Dict[PokepediaGeneration, List[PokepediaElementType]]:
        if jsonResponse is None:
            raise ValueError(f'jsonResponse argument is malformed: \"{jsonResponse}\"')

        typesJson = jsonResponse.get('types')
        if not utils.hasItems(typesJson):
            raise ValueError(f'\"types\" field in JSON response is null or empty: {jsonResponse}')

        currentTypes = list()
        for currentTypeJson in typesJson:
            currentTypes.append(PokepediaElementType.fromStr(currentTypeJson['type']['name']))

        pastTypesJson = jsonResponse.get('past_types')
        elementTypeGenerationDictionary = dict()

        if utils.hasItems(pastTypesJson):
            # TODO
            pass
        else:
            # TODO
            pass

        return elementTypeGenerationDictionary

    def __getEnDescription(self, jsonResponse: Dict) -> str:
        if not utils.hasItems(jsonResponse):
            raise ValueError(f'jsonResponse argument is malformed: \"{jsonResponse}\"')

        flavorTextEntries = jsonResponse.get('flavor_text_entries')
        if not utils.hasItems(flavorTextEntries):
            raise ValueError(f'\"flavor_text_entries\" field in JSON response is null or empty: {jsonResponse}')

        for flavorTextEntry in flavorTextEntries:
            if flavorTextEntry['language']['name'] == 'en':
                return utils.cleanStr(flavorTextEntry['flavor_text'])

        raise RuntimeError(f'can\'t find \"en\" language name in \"flavor_text_entries\" field: {jsonResponse}')

    def __getEnName(self, jsonResponse: Dict) -> str:
        if not utils.hasItems(jsonResponse):
            raise ValueError(f'jsonResponse argument is malformed: \"{jsonResponse}\"')

        names = jsonResponse.get('names')
        if not utils.hasItems(names):
            raise ValueError(f'\"names\" field in JSON response is null or empty: {jsonResponse}')

        for name in names:
            if name['language']['name'] == 'en':
                return utils.cleanStr(name['name'].title())

        raise RuntimeError(f'can\'t find \"en\" language name in \"names\" field: {jsonResponse}')

    def __getMoveGenerationDictionary(self, jsonResponse: Dict) -> Dict[PokepediaGeneration, PokepediaMoveGeneration]:
        if not utils.hasItems(jsonResponse):
            raise ValueError(f'jsonResponse argument is malformed: \"{jsonResponse}\"')

        moveGenerationDictionary = dict()

        # begin with current gen stats
        accuracy = jsonResponse['accuracy']
        power = jsonResponse['power']
        pp = jsonResponse['pp']
        damageClass = PokepediaDamageClass.fromStr(jsonResponse['damage_class']['name'])
        elementType = PokepediaElementType.fromStr(jsonResponse['type']['name'])
        move = None

        pastValues = jsonResponse['past_values']

        # iterate backwards and insert to dictionary once a gen is found. then 'un-patch' for
        # previous gens
        for pastValue in reversed(pastValues):
            generation = PokepediaGeneration.fromStr(pastValue['version_group']['name'])

            if damageClass is not PokepediaDamageClass.STATUS and generation.isEarlyGeneration():
                damageClass = PokepediaDamageClass.getTypeBasedDamageClass(elementType)

            move = PokepediaMoveGeneration(
                accuracy = accuracy,
                power = power,
                pp = pp,
                damageClass = damageClass,
                elementType = elementType,
                generation = generation
            )

            moveGenerationDictionary[generation] = move

            if utils.isValidNum(pastValue.get('accuracy')):
                accuracy = pastValue['accuracy']

            if utils.isValidNum(pastValue.get('power')):
                power = pastValue['power']

            if utils.isValidNum(pastValue.get('pp')):
                pp = pastValue['pp']

            if pastValue.get('type') is not None:
                elementType = PokepediaElementType.fromStr(pastValue['type']['name'])

        generation = PokepediaGeneration.fromStr(jsonResponse['generation']['name'])

        if damageClass is not PokepediaDamageClass.STATUS and generation.isEarlyGeneration():
            damageClass = PokepediaDamageClass.getTypeBasedDamageClass(elementType)

        move = PokepediaMoveGeneration(
            accuracy = accuracy,
            power = power,
            pp = pp,
            damageClass = damageClass,
            elementType = elementType,
            generation = generation
        )

        moveGenerationDictionary[generation] = move

        # scan for case where gen4+ type changed but not reflected in past_values JSON array
        if PokepediaGeneration.GENERATION_4 not in moveGenerationDictionary:
            if PokepediaGeneration.GENERATION_3 in moveGenerationDictionary:
                if moveGenerationDictionary[PokepediaGeneration.GENERATION_3].getDamageClass() != damageClass:
                    move = PokepediaMoveGeneration(
                        accuracy = moveGenerationDictionary[PokepediaGeneration.GENERATION_3].getAccuracy(),
                        power = moveGenerationDictionary[PokepediaGeneration.GENERATION_3].getPower(),
                        pp = moveGenerationDictionary[PokepediaGeneration.GENERATION_3].getPp(),
                        damageClass = damageClass,
                        elementType = moveGenerationDictionary[PokepediaGeneration.GENERATION_3].getElementType(),
                        generation = PokepediaGeneration.GENERATION_4
                    )

                    moveGenerationDictionary[PokepediaGeneration.GENERATION_4] = move
            elif PokepediaGeneration.GENERATION_2 in moveGenerationDictionary:
                if moveGenerationDictionary[PokepediaGeneration.GENERATION_2].getDamageClass() != damageClass:
                    move = PokepediaMoveGeneration(
                        accuracy = moveGenerationDictionary[PokepediaGeneration.GENERATION_2].getAccuracy(),
                        power = moveGenerationDictionary[PokepediaGeneration.GENERATION_2].getPower(),
                        pp = moveGenerationDictionary[PokepediaGeneration.GENERATION_2].getPp(),
                        damageClass = damageClass,
                        elementType = moveGenerationDictionary[PokepediaGeneration.GENERATION_2].getElementType(),
                        generation = PokepediaGeneration.GENERATION_4
                    )

                    moveGenerationDictionary[PokepediaGeneration.GENERATION_4] = move
            elif PokepediaGeneration.GENERATION_1 in moveGenerationDictionary:
                if moveGenerationDictionary[PokepediaGeneration.GENERATION_1].getDamageClass() != damageClass:
                    move = PokepediaMoveGeneration(
                        accuracy = moveGenerationDictionary[PokepediaGeneration.GENERATION_1].getAccuracy(),
                        power = moveGenerationDictionary[PokepediaGeneration.GENERATION_1].getPower(),
                        pp = moveGenerationDictionary[PokepediaGeneration.GENERATION_1].getPp(),
                        damageClass = damageClass,
                        elementType = moveGenerationDictionary[PokepediaGeneration.GENERATION_1].getElementType(),
                        generation = PokepediaGeneration.GENERATION_4
                    )

                    moveGenerationDictionary[PokepediaGeneration.GENERATION_4] = move

        # This loop goes through the dictionary of generational moves we've now built up and stored
        # within moveGenerationDictionary and removes any generations that are exact duplicates,
        # UNLESS there exists a generation between the between the duplicate(s) that is different.
        move = None
        for pokepediaGeneration in PokepediaGeneration:
            if pokepediaGeneration not in moveGenerationDictionary:
                continue
            elif move is None:
                move = moveGenerationDictionary[pokepediaGeneration]
            else:
                comparison = moveGenerationDictionary[pokepediaGeneration]

                if move.getAccuracy() == comparison.getAccuracy() and move.getDamageClass() == comparison.getDamageClass() and move.getElementType() == comparison.getElementType() and move.getPower() == comparison.getPower() and move.getPp() == comparison.getPp():
                    del moveGenerationDictionary[pokepediaGeneration]

                move = comparison

        return moveGenerationDictionary

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

        return PokepediaMove(
            generationMoves = self.__getMoveGenerationDictionary(jsonResponse),
            moveId = utils.getIntFromDict(jsonResponse, 'id'),
            description = self.__getEnDescription(jsonResponse),
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

        return PokepediaPokemon(
            generationElementTypes = self.__getElementTypeGenerationDictionary(jsonResponse),
            pokedexId = utils.getIntFromDict(jsonResponse, 'id'),
            name = jsonResponse['name'].title()
        )

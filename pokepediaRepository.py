import locale
from collections import Counter
from enum import Enum, auto
from json.decoder import JSONDecodeError
from typing import Dict, List

import requests
from requests import ConnectionError, HTTPError, Timeout
from requests.exceptions import ReadTimeout, TooManyRedirects
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

        text = text.lower()

        if text == 'bug':
            return PokepediaElementType.BUG
        elif text == 'dark':
            return PokepediaElementType.DARK
        elif text == 'dragon':
            return PokepediaElementType.DRAGON
        elif text == 'electric':
            return PokepediaElementType.ELECTRIC
        elif text == 'fairy':
            return PokepediaElementType.FAIRY
        elif text == 'fighting':
            return PokepediaElementType.FIGHTING
        elif text == 'fire':
            return PokepediaElementType.FIRE
        elif text == 'flying':
            return PokepediaElementType.FLYING
        elif text == 'ghost':
            return PokepediaElementType.GHOST
        elif text == 'grass':
            return PokepediaElementType.GRASS
        elif text == 'ground':
            return PokepediaElementType.GROUND
        elif text == 'ice':
            return PokepediaElementType.ICE
        elif text == 'normal':
            return PokepediaElementType.NORMAL
        elif text == 'poison':
            return PokepediaElementType.POISON
        elif text == 'psychic':
            return PokepediaElementType.PSYCHIC
        elif text == 'rock':
            return PokepediaElementType.ROCK
        elif text == 'steel':
            return PokepediaElementType.STEEL
        elif text == 'water':
            return PokepediaElementType.WATER
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

        text = text.lower()

        if text == 'physical':
            return PokepediaDamageClass.PHYSICAL
        elif text == 'special':
            return PokepediaDamageClass.SPECIAL
        elif text == 'status':
            return PokepediaDamageClass.STATUS
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
            return PokepediaDamageClass.PHYSICAL
        elif elementType in specialElementTypes:
            return PokepediaDamageClass.SPECIAL
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

    def getEffectDescription(self) -> str:
        if self is PokepediaDamageMultiplier.ZERO:
            return 'damage from'
        elif self is PokepediaDamageMultiplier.ZERO_POINT_TWO_FIVE or self is PokepediaDamageMultiplier.ZERO_POINT_FIVE:
            return 'resistant to'
        elif self is PokepediaDamageMultiplier.ONE:
            raise RuntimeError(f'{self} should not be used with this method!')
        elif self is PokepediaDamageMultiplier.TWO or self is PokepediaDamageMultiplier.FOUR:
            return 'weak to'
        else:
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
    def fromPokedexId(cls, pokedexId: int):
        if not utils.isValidNum(pokedexId):
            raise ValueError(f'pokedexId argument is malformed: \"{pokedexId}\"')
        elif pokedexId < 0:
            raise ValueError(f'pokedexId argument is out of bounds: \"{pokedexId}\"')

        if pokedexId < 152:
            return PokepediaGeneration.GENERATION_1
        elif pokedexId < 252:
            return PokepediaGeneration.GENERATION_2
        elif pokedexId < 387:
            return PokepediaGeneration.GENERATION_3
        elif pokedexId < 494:
            return PokepediaGeneration.GENERATION_4
        elif pokedexId < 650:
            return PokepediaGeneration.GENERATION_5
        elif pokedexId < 722:
            return PokepediaGeneration.GENERATION_6
        elif pokedexId < 810:
            return PokepediaGeneration.GENERATION_7
        else:
            return PokepediaGeneration.GENERATION_8

    @classmethod
    def fromStr(cls, text: str):
        if not utils.isValidStr(text):
            raise ValueError(f'text argument is malformed: \"{text}\"')

        text = text.lower()

        if text == 'gold-silver' or text == 'crystal' or text == 'generation-ii':
            return PokepediaGeneration.GENERATION_2
        elif text == 'ruby-sapphire' or text == 'emerald' or text == 'firered-leafgreen' or text == 'generation-iii':
            return PokepediaGeneration.GENERATION_3
        elif text == 'diamond-pearl' or text == 'platinum' or text == 'heartgold-soulsilver' or text == 'generation-iv':
            return PokepediaGeneration.GENERATION_4
        elif text == 'black-white' or text == 'black-2-white-2' or text == 'generation-v':
            return PokepediaGeneration.GENERATION_5
        elif text == 'x-y' or text == 'omega-ruby-alpha-sapphire' or text == 'generation-vi':
            return PokepediaGeneration.GENERATION_6
        elif text == 'sun-moon' or text == 'ultra-sun-ultra-moon' or text == 'generation-vii':
            return PokepediaGeneration.GENERATION_7
        elif text == 'sword-shield' or text == 'brilliant-diamond-shining-pearl' or text == 'generation-viii':
            return PokepediaGeneration.GENERATION_8
        else:
            return PokepediaGeneration.GENERATION_1

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

        self.__accuracy: int = accuracy
        self.__power: int = power
        self.__pp: int = pp
        self.__damageClass: PokepediaDamageClass = damageClass
        self.__elementType: PokepediaElementType = elementType
        self.__generation: PokepediaGeneration = generation

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

        genMoveStrings: List[str] = list()

        for gen in PokepediaGeneration:
            if gen in self.__generationMoves:
                genMove = self.__generationMoves[gen]
                genMoveStrings.append(genMove.toStr())

        genMoveString = delimiter.join(genMoveStrings)
        return f'{self.getName()} — {genMoveString}'

    def toStrList(self) -> List[str]:
        strings: List[str] = list()
        strings.append(f'{self.getName()} — {self.getDescription()}')

        for gen in PokepediaGeneration:
            if gen in self.__generationMoves:
                genMove = self.__generationMoves[gen]
                strings.append(genMove.toStr())

        return strings


class PokepediaTypeChart(Enum):

    GENERATION_1 = auto()
    GENERATION_2_THRU_5 = auto()
    GENERATION_6_AND_ON = auto()

    def __buildDictionaryFromWeaknessesAndResistances(
        self,
        noEffect: List[PokepediaElementType],
        resistances: List[PokepediaElementType],
        weaknesses: List[PokepediaElementType]
    ) -> Dict[PokepediaDamageMultiplier, List[PokepediaElementType]]:
        if noEffect is None:
            raise ValueError(f'noEffect argument is malformed: \"{noEffect}\"')
        elif resistances is None:
            raise ValueError(f'resistances argument is malformed: \"{resistances}\"')
        if weaknesses is None:
            raise ValueError(f'noEffect argument is malformed: \"{weaknesses}\"')

        for elementType in noEffect:
            while elementType in resistances:
                resistances.remove(elementType)

            while elementType in weaknesses:
                weaknesses.remove(elementType)

        noEffect.sort(key = lambda elementType: elementType.value)

        elementsToFullyRemove: List[PokepediaElementType] = list()
        for elementType in resistances:
            if elementType in weaknesses:
                elementsToFullyRemove.append(elementType)

        for elementToFullyRemove in elementsToFullyRemove:
            while elementToFullyRemove in resistances:
                resistances.remove(elementToFullyRemove)

            while elementToFullyRemove in weaknesses:
                weaknesses.remove(elementToFullyRemove)

        resistances.sort(key = lambda elementType: elementType.value)
        weaknesses.sort(key = lambda elementType: elementType.value)

        dictionary: Dict[PokepediaDamageMultiplier, List[PokepediaElementType]] = dict()

        if utils.hasItems(noEffect):
            dictionary[PokepediaDamageMultiplier.ZERO] = noEffect

        if utils.hasItems(resistances):
            counter = Counter(resistances)
            regularResistances: List[PokepediaElementType] = list()
            doubleResistances: List[PokepediaElementType] = list()

            for elementType in PokepediaElementType:
                if elementType in counter:
                    if counter[elementType] == 1:
                        regularResistances.append(elementType)
                    elif counter[elementType] == 2:
                        doubleResistances.append(elementType)
                    else:
                        raise RuntimeError(f'illegal counter value ({counter[elementType]}) for {elementType}')

            if utils.hasItems(regularResistances):
                dictionary[PokepediaDamageMultiplier.ZERO_POINT_FIVE] = regularResistances

            if utils.hasItems(doubleResistances):
                dictionary[PokepediaDamageMultiplier.ZERO_POINT_TWO_FIVE] = doubleResistances

        if utils.hasItems(weaknesses):
            counter = Counter(weaknesses)
            regularWeaknesses: List[PokepediaElementType] = list()
            doubleWeaknesses: List[PokepediaElementType] = list()

            for elementType in PokepediaElementType:
                if elementType in counter:
                    if counter[elementType] == 1:
                        regularWeaknesses.append(elementType)
                    elif counter[elementType] == 2:
                        doubleWeaknesses.append(elementType)
                    else:
                        raise RuntimeError(f'illegal counter value ({counter[elementType]}) for {elementType}')

            if utils.hasItems(regularWeaknesses):
                dictionary[PokepediaDamageMultiplier.TWO] = regularWeaknesses

            if utils.hasItems(doubleWeaknesses):
                dictionary[PokepediaDamageMultiplier.FOUR] = doubleWeaknesses

        return dictionary

    @classmethod
    def fromPokepediaGeneration(cls, pokepediaGeneration: PokepediaGeneration):
        if pokepediaGeneration is None:
            raise ValueError(f'pokepediaGeneration argument is malformed: \"{pokepediaGeneration}\"')

        if pokepediaGeneration is PokepediaGeneration.GENERATION_1:
            return PokepediaTypeChart.GENERATION_1
        elif pokepediaGeneration is PokepediaGeneration.GENERATION_2 or pokepediaGeneration is PokepediaGeneration.GENERATION_3 or pokepediaGeneration is PokepediaGeneration.GENERATION_4 or pokepediaGeneration is PokepediaGeneration.GENERATION_5:
            return PokepediaTypeChart.GENERATION_2_THRU_5
        else:
            return PokepediaTypeChart.GENERATION_6_AND_ON

    def __getGenerationOneWeaknessesAndResistancesFor(self, types: List[PokepediaElementType]) -> Dict[PokepediaDamageMultiplier, List[PokepediaElementType]]:
        if not utils.hasItems(types):
            raise ValueError(f'types argument is malformed: \"{types}\"')

        noEffect: List[PokepediaElementType] = list()
        resistances: List[PokepediaElementType] = list()
        weaknesses: List[PokepediaElementType] = list()

        for elementType in types:
            if elementType is PokepediaElementType.BUG:
                resistances.append(PokepediaElementType.FIGHTING)
                resistances.append(PokepediaElementType.GRASS)
                resistances.append(PokepediaElementType.GROUND)
                weaknesses.append(PokepediaElementType.FIRE)
                weaknesses.append(PokepediaElementType.FLYING)
                weaknesses.append(PokepediaElementType.POISON)
                weaknesses.append(PokepediaElementType.ROCK)
            elif elementType is PokepediaElementType.DARK:
                raise ValueError(f'illegal PokepediaElementType for this type chart ({self}): \"{elementType}\"')
            elif elementType is PokepediaElementType.DRAGON:
                resistances.append(PokepediaElementType.ELECTRIC)
                resistances.append(PokepediaElementType.FIRE)
                resistances.append(PokepediaElementType.GRASS)
                resistances.append(PokepediaElementType.WATER)
                weaknesses.append(PokepediaElementType.DRAGON)
                weaknesses.append(PokepediaElementType.ICE)
            elif elementType is PokepediaElementType.ELECTRIC:
                resistances.append(PokepediaElementType.ELECTRIC)
                resistances.append(PokepediaElementType.FLYING)
                weaknesses.append(PokepediaElementType.GROUND)
            elif elementType is PokepediaElementType.FAIRY:
                raise ValueError(f'illegal PokepediaElementType for this type chart ({self}): \"{elementType}\"')
            elif elementType is PokepediaElementType.FIGHTING:
                resistances.append(PokepediaElementType.BUG)
                resistances.append(PokepediaElementType.ROCK)
                weaknesses.append(PokepediaElementType.FLYING)
                weaknesses.append(PokepediaElementType.PSYCHIC)
            elif elementType is PokepediaElementType.FIRE:
                resistances.append(PokepediaElementType.BUG)
                resistances.append(PokepediaElementType.FIRE)
                resistances.append(PokepediaElementType.GRASS)
                weaknesses.append(PokepediaElementType.GROUND)
                weaknesses.append(PokepediaElementType.ROCK)
                weaknesses.append(PokepediaElementType.WATER)
            elif elementType is PokepediaElementType.FLYING:
                noEffect.append(PokepediaElementType.GROUND)
                resistances.append(PokepediaElementType.BUG)
                resistances.append(PokepediaElementType.FIGHTING)
                resistances.append(PokepediaElementType.GRASS)
                weaknesses.append(PokepediaElementType.ELECTRIC)
                weaknesses.append(PokepediaElementType.ICE)
                weaknesses.append(PokepediaElementType.ROCK)
            elif elementType is PokepediaElementType.GHOST:
                noEffect.append(PokepediaElementType.FIGHTING)
                noEffect.append(PokepediaElementType.NORMAL)
                resistances.append(PokepediaElementType.BUG)
                resistances.append(PokepediaElementType.POISON)
                weaknesses.append(PokepediaElementType.GHOST)
            elif elementType is PokepediaElementType.GRASS:
                resistances.append(PokepediaElementType.ELECTRIC)
                resistances.append(PokepediaElementType.GRASS)
                resistances.append(PokepediaElementType.GROUND)
                resistances.append(PokepediaElementType.WATER)
                weaknesses.append(PokepediaElementType.BUG)
                weaknesses.append(PokepediaElementType.FIRE)
                weaknesses.append(PokepediaElementType.FLYING)
                weaknesses.append(PokepediaElementType.ICE)
                weaknesses.append(PokepediaElementType.POISON)
            elif elementType is PokepediaElementType.GROUND:
                noEffect.append(PokepediaElementType.ELECTRIC)
                resistances.append(PokepediaElementType.POISON)
                resistances.append(PokepediaElementType.ROCK)
                weaknesses.append(PokepediaElementType.GRASS)
                weaknesses.append(PokepediaElementType.ICE)
                weaknesses.append(PokepediaElementType.WATER)
            elif elementType is PokepediaElementType.ICE:
                resistances.append(PokepediaElementType.ICE)
                weaknesses.append(PokepediaElementType.FIGHTING)
                weaknesses.append(PokepediaElementType.FIRE)
                weaknesses.append(PokepediaElementType.ROCK)
            elif elementType is PokepediaElementType.NORMAL:
                noEffect.append(PokepediaElementType.GHOST)
                weaknesses.append(PokepediaElementType.FIGHTING)
            elif elementType is PokepediaElementType.POISON:
                resistances.append(PokepediaElementType.FIGHTING)
                resistances.append(PokepediaElementType.GRASS)
                resistances.append(PokepediaElementType.POISON)
                weaknesses.append(PokepediaElementType.BUG)
                weaknesses.append(PokepediaElementType.GROUND)
                weaknesses.append(PokepediaElementType.PSYCHIC)
            elif elementType is PokepediaElementType.PSYCHIC:
                noEffect.append(PokepediaElementType.GHOST)
                resistances.append(PokepediaElementType.FIGHTING)
                resistances.append(PokepediaElementType.PSYCHIC)
                weaknesses.append(PokepediaElementType.BUG)
            elif elementType is PokepediaElementType.ROCK:
                resistances.append(PokepediaElementType.FIRE)
                resistances.append(PokepediaElementType.FLYING)
                resistances.append(PokepediaElementType.NORMAL)
                resistances.append(PokepediaElementType.POISON)
                weaknesses.append(PokepediaElementType.FIGHTING)
                weaknesses.append(PokepediaElementType.GRASS)
                weaknesses.append(PokepediaElementType.GROUND)
                weaknesses.append(PokepediaElementType.WATER)
            elif elementType is PokepediaElementType.STEEL:
                raise ValueError(f'illegal PokepediaElementType for this type chart ({self}): \"{elementType}\"')
            elif elementType is PokepediaElementType.WATER:
                resistances.append(PokepediaElementType.FIRE)
                resistances.append(PokepediaElementType.ICE)
                resistances.append(PokepediaElementType.WATER)
                weaknesses.append(PokepediaElementType.ELECTRIC)
                weaknesses.append(PokepediaElementType.GRASS)

        return self.__buildDictionaryFromWeaknessesAndResistances(
            noEffect = noEffect,
            resistances = resistances,
            weaknesses = weaknesses
        )

    def __getGenerationTwoThruFiveWeaknessesAndResistancesFor(self, types: List[PokepediaElementType]) -> Dict[PokepediaDamageMultiplier, List[PokepediaElementType]]:
        if not utils.hasItems(types):
            raise ValueError(f'types argument is malformed: \"{types}\"')

        noEffect: List[PokepediaElementType] = list()
        resistances: List[PokepediaElementType] = list()
        weaknesses: List[PokepediaElementType] = list()

        for elementType in types:
            if elementType is PokepediaElementType.BUG:
                resistances.append(PokepediaElementType.FIGHTING)
                resistances.append(PokepediaElementType.GRASS)
                resistances.append(PokepediaElementType.GROUND)
                weaknesses.append(PokepediaElementType.FIRE)
                weaknesses.append(PokepediaElementType.FLYING)
                weaknesses.append(PokepediaElementType.POISON)
                weaknesses.append(PokepediaElementType.ROCK)
            elif elementType is PokepediaElementType.DARK:
                noEffect.append(PokepediaElementType.PSYCHIC)
                resistances.append(PokepediaElementType.DARK)
                resistances.append(PokepediaElementType.GHOST)
                weaknesses.append(PokepediaElementType.BUG)
                weaknesses.append(PokepediaElementType.FIGHTING)
            elif elementType is PokepediaElementType.DRAGON:
                resistances.append(PokepediaElementType.ELECTRIC)
                resistances.append(PokepediaElementType.FIRE)
                resistances.append(PokepediaElementType.GRASS)
                resistances.append(PokepediaElementType.WATER)
                weaknesses.append(PokepediaElementType.DRAGON)
                weaknesses.append(PokepediaElementType.ICE)
            elif elementType is PokepediaElementType.ELECTRIC:
                resistances.append(PokepediaElementType.ELECTRIC)
                resistances.append(PokepediaElementType.FLYING)
                resistances.append(PokepediaElementType.STEEL)
                weaknesses.append(PokepediaElementType.GROUND)
            elif elementType is PokepediaElementType.FAIRY:
                raise ValueError(f'illegal PokepediaElementType for this type chart ({self}): \"{elementType}\"')
            elif elementType is PokepediaElementType.FIGHTING:
                resistances.append(PokepediaElementType.BUG)
                resistances.append(PokepediaElementType.DARK)
                resistances.append(PokepediaElementType.ROCK)
                weaknesses.append(PokepediaElementType.FLYING)
                weaknesses.append(PokepediaElementType.PSYCHIC)
            elif elementType is PokepediaElementType.FIRE:
                resistances.append(PokepediaElementType.BUG)
                resistances.append(PokepediaElementType.FIRE)
                resistances.append(PokepediaElementType.ICE)
                resistances.append(PokepediaElementType.GRASS)
                resistances.append(PokepediaElementType.STEEL)
                weaknesses.append(PokepediaElementType.GROUND)
                weaknesses.append(PokepediaElementType.ROCK)
                weaknesses.append(PokepediaElementType.WATER)
            elif elementType is PokepediaElementType.FLYING:
                noEffect.append(PokepediaElementType.GROUND)
                resistances.append(PokepediaElementType.BUG)
                resistances.append(PokepediaElementType.FIGHTING)
                resistances.append(PokepediaElementType.GRASS)
                weaknesses.append(PokepediaElementType.ELECTRIC)
                weaknesses.append(PokepediaElementType.ICE)
                weaknesses.append(PokepediaElementType.ROCK)
            elif elementType is PokepediaElementType.GHOST:
                noEffect.append(PokepediaElementType.FIGHTING)
                noEffect.append(PokepediaElementType.NORMAL)
                resistances.append(PokepediaElementType.BUG)
                resistances.append(PokepediaElementType.POISON)
                weaknesses.append(PokepediaElementType.DARK)
                weaknesses.append(PokepediaElementType.GHOST)
            elif elementType is PokepediaElementType.GRASS:
                resistances.append(PokepediaElementType.ELECTRIC)
                resistances.append(PokepediaElementType.GRASS)
                resistances.append(PokepediaElementType.GROUND)
                resistances.append(PokepediaElementType.WATER)
                weaknesses.append(PokepediaElementType.BUG)
                weaknesses.append(PokepediaElementType.FIRE)
                weaknesses.append(PokepediaElementType.FLYING)
                weaknesses.append(PokepediaElementType.ICE)
                weaknesses.append(PokepediaElementType.POISON)
            elif elementType is PokepediaElementType.GROUND:
                noEffect.append(PokepediaElementType.ELECTRIC)
                resistances.append(PokepediaElementType.POISON)
                resistances.append(PokepediaElementType.ROCK)
                weaknesses.append(PokepediaElementType.GRASS)
                weaknesses.append(PokepediaElementType.ICE)
                weaknesses.append(PokepediaElementType.WATER)
            elif elementType is PokepediaElementType.ICE:
                resistances.append(PokepediaElementType.ICE)
                weaknesses.append(PokepediaElementType.FIGHTING)
                weaknesses.append(PokepediaElementType.FIRE)
                weaknesses.append(PokepediaElementType.ROCK)
                weaknesses.append(PokepediaElementType.STEEL)
            elif elementType is PokepediaElementType.NORMAL:
                noEffect.append(PokepediaElementType.GHOST)
                weaknesses.append(PokepediaElementType.FIGHTING)
            elif elementType is PokepediaElementType.POISON:
                resistances.append(PokepediaElementType.BUG)
                resistances.append(PokepediaElementType.FIGHTING)
                resistances.append(PokepediaElementType.GRASS)
                resistances.append(PokepediaElementType.POISON)
                weaknesses.append(PokepediaElementType.GROUND)
                weaknesses.append(PokepediaElementType.PSYCHIC)
            elif elementType is PokepediaElementType.PSYCHIC:
                resistances.append(PokepediaElementType.FIGHTING)
                resistances.append(PokepediaElementType.PSYCHIC)
                weaknesses.append(PokepediaElementType.BUG)
                weaknesses.append(PokepediaElementType.DARK)
                weaknesses.append(PokepediaElementType.GHOST)
            elif elementType is PokepediaElementType.ROCK:
                resistances.append(PokepediaElementType.FIRE)
                resistances.append(PokepediaElementType.FLYING)
                resistances.append(PokepediaElementType.NORMAL)
                resistances.append(PokepediaElementType.POISON)
                weaknesses.append(PokepediaElementType.FIGHTING)
                weaknesses.append(PokepediaElementType.GRASS)
                weaknesses.append(PokepediaElementType.GROUND)
                weaknesses.append(PokepediaElementType.WATER)
            elif elementType is PokepediaElementType.STEEL:
                noEffect.append(PokepediaElementType.POISON)
                resistances.append(PokepediaElementType.BUG)
                resistances.append(PokepediaElementType.DARK)
                resistances.append(PokepediaElementType.DRAGON)
                resistances.append(PokepediaElementType.FLYING)
                resistances.append(PokepediaElementType.GHOST)
                resistances.append(PokepediaElementType.GRASS)
                resistances.append(PokepediaElementType.ICE)
                resistances.append(PokepediaElementType.NORMAL)
                resistances.append(PokepediaElementType.PSYCHIC)
                resistances.append(PokepediaElementType.ROCK)
                resistances.append(PokepediaElementType.STEEL)
                weaknesses.append(PokepediaElementType.FIGHTING)
                weaknesses.append(PokepediaElementType.FIRE)
                weaknesses.append(PokepediaElementType.GROUND)
            elif elementType is PokepediaElementType.WATER:
                resistances.append(PokepediaElementType.FIRE)
                resistances.append(PokepediaElementType.ICE)
                resistances.append(PokepediaElementType.STEEL)
                resistances.append(PokepediaElementType.WATER)
                weaknesses.append(PokepediaElementType.ELECTRIC)
                weaknesses.append(PokepediaElementType.GRASS)

        return self.__buildDictionaryFromWeaknessesAndResistances(
            noEffect = noEffect,
            resistances = resistances,
            weaknesses = weaknesses
        )

    def __getGenerationSixAndOnWeaknessesAndResistancesFor(self, types: List[PokepediaElementType]) -> Dict[PokepediaDamageMultiplier, List[PokepediaElementType]]:
        if not utils.hasItems(types):
            raise ValueError(f'types argument is malformed: \"{types}\"')

        noEffect: List[PokepediaElementType] = list()
        resistances: List[PokepediaElementType] = list()
        weaknesses: List[PokepediaElementType] = list()

        for elementType in types:
            if elementType is PokepediaElementType.BUG:
                resistances.append(PokepediaElementType.FIGHTING)
                resistances.append(PokepediaElementType.GRASS)
                resistances.append(PokepediaElementType.GROUND)
                weaknesses.append(PokepediaElementType.FIRE)
                weaknesses.append(PokepediaElementType.FLYING)
                weaknesses.append(PokepediaElementType.POISON)
                weaknesses.append(PokepediaElementType.ROCK)
            elif elementType is PokepediaElementType.DARK:
                noEffect.append(PokepediaElementType.PSYCHIC)
                resistances.append(PokepediaElementType.DARK)
                resistances.append(PokepediaElementType.GHOST)
                weaknesses.append(PokepediaElementType.BUG)
                weaknesses.append(PokepediaElementType.FIGHTING)
            elif elementType is PokepediaElementType.DRAGON:
                resistances.append(PokepediaElementType.ELECTRIC)
                resistances.append(PokepediaElementType.FIRE)
                resistances.append(PokepediaElementType.GRASS)
                resistances.append(PokepediaElementType.WATER)
                weaknesses.append(PokepediaElementType.DRAGON)
                weaknesses.append(PokepediaElementType.ICE)
            elif elementType is PokepediaElementType.ELECTRIC:
                resistances.append(PokepediaElementType.ELECTRIC)
                resistances.append(PokepediaElementType.FLYING)
                resistances.append(PokepediaElementType.STEEL)
                weaknesses.append(PokepediaElementType.GROUND)
            elif elementType is PokepediaElementType.FAIRY:
                noEffect.append(PokepediaElementType.DRAGON)
                resistances.append(PokepediaElementType.BUG)
                resistances.append(PokepediaElementType.DARK)
                resistances.append(PokepediaElementType.FIGHTING)
                weaknesses.append(PokepediaElementType.POISON)
                weaknesses.append(PokepediaElementType.STEEL)
            elif elementType is PokepediaElementType.FIGHTING:
                resistances.append(PokepediaElementType.BUG)
                resistances.append(PokepediaElementType.DARK)
                resistances.append(PokepediaElementType.ROCK)
                weaknesses.append(PokepediaElementType.FLYING)
                weaknesses.append(PokepediaElementType.PSYCHIC)
            elif elementType is PokepediaElementType.FIRE:
                resistances.append(PokepediaElementType.BUG)
                resistances.append(PokepediaElementType.FIRE)
                resistances.append(PokepediaElementType.ICE)
                resistances.append(PokepediaElementType.GRASS)
                resistances.append(PokepediaElementType.STEEL)
                weaknesses.append(PokepediaElementType.GROUND)
                weaknesses.append(PokepediaElementType.ROCK)
                weaknesses.append(PokepediaElementType.WATER)
            elif elementType is PokepediaElementType.FLYING:
                noEffect.append(PokepediaElementType.GROUND)
                resistances.append(PokepediaElementType.BUG)
                resistances.append(PokepediaElementType.FIGHTING)
                resistances.append(PokepediaElementType.GRASS)
                weaknesses.append(PokepediaElementType.ELECTRIC)
                weaknesses.append(PokepediaElementType.ICE)
                weaknesses.append(PokepediaElementType.ROCK)
            elif elementType is PokepediaElementType.GHOST:
                noEffect.append(PokepediaElementType.FIGHTING)
                noEffect.append(PokepediaElementType.NORMAL)
                resistances.append(PokepediaElementType.BUG)
                resistances.append(PokepediaElementType.POISON)
                weaknesses.append(PokepediaElementType.DARK)
                weaknesses.append(PokepediaElementType.GHOST)
            elif elementType is PokepediaElementType.GRASS:
                resistances.append(PokepediaElementType.ELECTRIC)
                resistances.append(PokepediaElementType.GRASS)
                resistances.append(PokepediaElementType.GROUND)
                resistances.append(PokepediaElementType.WATER)
                weaknesses.append(PokepediaElementType.BUG)
                weaknesses.append(PokepediaElementType.FIRE)
                weaknesses.append(PokepediaElementType.FLYING)
                weaknesses.append(PokepediaElementType.ICE)
                weaknesses.append(PokepediaElementType.POISON)
            elif elementType is PokepediaElementType.GROUND:
                noEffect.append(PokepediaElementType.ELECTRIC)
                resistances.append(PokepediaElementType.POISON)
                resistances.append(PokepediaElementType.ROCK)
                weaknesses.append(PokepediaElementType.GRASS)
                weaknesses.append(PokepediaElementType.ICE)
                weaknesses.append(PokepediaElementType.WATER)
            elif elementType is PokepediaElementType.ICE:
                resistances.append(PokepediaElementType.ICE)
                weaknesses.append(PokepediaElementType.FIGHTING)
                weaknesses.append(PokepediaElementType.FIRE)
                weaknesses.append(PokepediaElementType.ROCK)
                weaknesses.append(PokepediaElementType.STEEL)
            elif elementType is PokepediaElementType.NORMAL:
                noEffect.append(PokepediaElementType.GHOST)
                weaknesses.append(PokepediaElementType.FIGHTING)
            elif elementType is PokepediaElementType.POISON:
                resistances.append(PokepediaElementType.FIGHTING)
                resistances.append(PokepediaElementType.GRASS)
                resistances.append(PokepediaElementType.POISON)
                weaknesses.append(PokepediaElementType.GROUND)
                weaknesses.append(PokepediaElementType.PSYCHIC)
            elif elementType is PokepediaElementType.PSYCHIC:
                resistances.append(PokepediaElementType.FIGHTING)
                resistances.append(PokepediaElementType.PSYCHIC)
                weaknesses.append(PokepediaElementType.BUG)
                weaknesses.append(PokepediaElementType.DARK)
                weaknesses.append(PokepediaElementType.GHOST)
            elif elementType is PokepediaElementType.ROCK:
                resistances.append(PokepediaElementType.FIRE)
                resistances.append(PokepediaElementType.FLYING)
                resistances.append(PokepediaElementType.NORMAL)
                resistances.append(PokepediaElementType.POISON)
                weaknesses.append(PokepediaElementType.FIGHTING)
                weaknesses.append(PokepediaElementType.GRASS)
                weaknesses.append(PokepediaElementType.GROUND)
                weaknesses.append(PokepediaElementType.WATER)
            elif elementType is PokepediaElementType.STEEL:
                noEffect.append(PokepediaElementType.POISON)
                resistances.append(PokepediaElementType.BUG)
                resistances.append(PokepediaElementType.DRAGON)
                resistances.append(PokepediaElementType.FLYING)
                resistances.append(PokepediaElementType.GRASS)
                resistances.append(PokepediaElementType.ICE)
                resistances.append(PokepediaElementType.NORMAL)
                resistances.append(PokepediaElementType.PSYCHIC)
                resistances.append(PokepediaElementType.ROCK)
                resistances.append(PokepediaElementType.STEEL)
                weaknesses.append(PokepediaElementType.FIGHTING)
                weaknesses.append(PokepediaElementType.FIRE)
                weaknesses.append(PokepediaElementType.GROUND)
            elif elementType is PokepediaElementType.WATER:
                resistances.append(PokepediaElementType.FIRE)
                resistances.append(PokepediaElementType.ICE)
                resistances.append(PokepediaElementType.STEEL)
                resistances.append(PokepediaElementType.WATER)
                weaknesses.append(PokepediaElementType.ELECTRIC)
                weaknesses.append(PokepediaElementType.GRASS)

        return self.__buildDictionaryFromWeaknessesAndResistances(
            noEffect = noEffect,
            resistances = resistances,
            weaknesses = weaknesses
        )

    def getWeaknessesAndResistancesFor(self, types: List[PokepediaElementType]) -> Dict[PokepediaDamageMultiplier, List[PokepediaElementType]]:
        if not utils.hasItems(types):
            raise ValueError(f'types argument is malformed: \"{types}\"')

        if self is PokepediaTypeChart.GENERATION_1:
            return self.__getGenerationOneWeaknessesAndResistancesFor(types)
        elif self is PokepediaTypeChart.GENERATION_2_THRU_5:
            return self.__getGenerationTwoThruFiveWeaknessesAndResistancesFor(types)
        elif self is PokepediaTypeChart.GENERATION_6_AND_ON:
            return self.__getGenerationSixAndOnWeaknessesAndResistancesFor(types)
        else:
            raise RuntimeError(f'unknown PokepediaTypeChart: \"{self}\"')


class PokepediaPokemon():

    def __init__(
        self,
        generationElementTypes: Dict[PokepediaGeneration, List[PokepediaElementType]],
        initialGeneration: PokepediaGeneration,
        height: int,
        pokedexId: int,
        weight: int,
        name: str
    ):
        if not utils.hasItems(generationElementTypes):
            raise ValueError(f'generationElementTypes argument is malformed: \"{generationElementTypes}\"')
        elif initialGeneration is None:
            raise ValueError(f'initialGeneration argument is malformed: \"{initialGeneration}\"')
        elif not utils.isValidNum(height):
            raise ValueError(f'height argument is malformed: \"{height}\"')
        elif not utils.isValidNum(pokedexId):
            raise ValueError(f'pokedexId argument is malformed: \"{pokedexId}\"')
        elif not utils.isValidNum(weight):
            raise ValueError(f'weight argument is malformed: \"{weight}\"')
        elif not utils.isValidStr(name):
            raise ValueError(f'name argument is malformed: \"{name}\"')

        self.__generationElementTypes = generationElementTypes
        self.__initialGeneration = initialGeneration
        self.__height = height
        self.__pokedexId = pokedexId
        self.__weight = weight
        self.__name = name

    def __buildGenerationElementTypesWeaknessesAndResistancesStr(
        self,
        weaknessesAndResistances: Dict[PokepediaDamageMultiplier, List[PokepediaElementType]],
        damageMultiplier: PokepediaDamageMultiplier,
        delimiter: str
    ) -> str:
        if not utils.hasItems(weaknessesAndResistances):
            raise ValueError(f'weaknessesAndResistances argument is malformed: \"{weaknessesAndResistances}\"')
        elif damageMultiplier is None:
            raise ValueError(f'damageMultiplier argument is malformed: \"{damageMultiplier}\"')
        elif delimiter is None:
            raise ValueError(f'delimiter argument is malformed: \"{delimiter}\"')

        if damageMultiplier not in weaknessesAndResistances or not utils.hasItems(weaknessesAndResistances[damageMultiplier]):
            return None

        elementTypesStrings: List[str] = list()
        for elementType in weaknessesAndResistances[damageMultiplier]:
            elementTypesStrings.append(elementType.getEmojiOrStr().lower())

        elementTypesString = delimiter.join(elementTypesStrings)
        return f'{damageMultiplier.toStr()} {damageMultiplier.getEffectDescription()} {elementTypesString}.'

    def getGenerationElementTypes(self) -> Dict[PokepediaGeneration, List[PokepediaElementType]]:
        return self.__generationElementTypes

    def getHeight(self) -> int:
        return self.__height

    def getHeightStr(self) -> str:
        return locale.format_string("%d", self.__height, grouping = True)

    def getInitialGeneration(self) -> PokepediaGeneration:
        return self.__initialGeneration

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

    def toStrList(self, delimiter: str = ', ') -> List[str]:
        if delimiter is None:
            raise ValueError(f'delimiter argument is malformed: \"{delimiter}\"')

        strings: List[str] = list()
        strings.append(f'{self.__name} (#{self.getPokedexIdStr()}) — introduced in {self.__initialGeneration.toStr()}, weight is {self.getWeightStr()} and height is {self.getHeightStr()}.')

        for gen in PokepediaGeneration:
            if gen in self.__generationElementTypes:
                genElementTypes = self.__generationElementTypes[gen]

                genElementTypesStrings: List[str] = list()
                for genElementType in genElementTypes:
                    genElementTypesStrings.append(genElementType.toStr().lower())

                genElementTypesString = delimiter.join(genElementTypesStrings)
                message = f'{gen.toStr()} ({genElementTypesString}):'

                typeChart = PokepediaTypeChart.fromPokepediaGeneration(gen)
                weaknessesAndResistances = typeChart.getWeaknessesAndResistancesFor(genElementTypes)

                for damageMultiplier in PokepediaDamageMultiplier:
                    if damageMultiplier is PokepediaDamageMultiplier.ONE:
                        continue

                    damageMultiplierMessage = self.__buildGenerationElementTypesWeaknessesAndResistancesStr(
                        weaknessesAndResistances = weaknessesAndResistances,
                        damageMultiplier = damageMultiplier,
                        delimiter = delimiter
                    )

                    if utils.isValidStr(damageMultiplierMessage):
                        message = f'{message} {damageMultiplierMessage}'

                strings.append(message)

        return strings


class PokepediaRepository():

    def __init__(self):
        pass

    def __getElementTypeGenerationDictionary(
        self,
        jsonResponse: Dict,
        initialGeneration: PokepediaGeneration
    ) -> Dict[PokepediaGeneration, List[PokepediaElementType]]:
        if jsonResponse is None:
            raise ValueError(f'jsonResponse argument is malformed: \"{jsonResponse}\"')
        elif initialGeneration is None:
            raise ValueError(f'initialGeneration argument is malformed: \"{initialGeneration}\"')

        currentTypesJson = jsonResponse.get('types')
        if not utils.hasItems(currentTypesJson):
            raise ValueError(f'\"types\" field in JSON response is null or empty: {jsonResponse}')

        # begin with current generation types
        currentTypesList: List[PokepediaElementType] = list()
        for currentTypeJson in currentTypesJson:
            currentTypesList.append(PokepediaElementType.fromStr(currentTypeJson['type']['name']))

        pastTypesJson = jsonResponse.get('past_types')
        if pastTypesJson is None:
            raise ValueError(f'\"past_types\" field in JSON response is null: {jsonResponse}')

        elementTypeGenerationDictionary: Dict[PokepediaGeneration, List[PokepediaElementType]] = dict()

        # iterate backwards and insert into dictionary once a generation is found.
        # then 'un-patch' for previous generations.
        for pokepediaGeneration in reversed(PokepediaGeneration):
            for pastTypeJson in pastTypesJson:
                generation = PokepediaGeneration.fromStr(pastTypeJson['generation']['name'])

                if generation == pokepediaGeneration:
                    currentTypesList: List[PokepediaElementType] = list()

                    typesJson = pastTypeJson.get('types')
                    if not utils.hasItems(typesJson):
                        raise ValueError(f'\"types\" field in \"past_types\" JSON array is null or empty: {jsonResponse}')

                    for typeJson in typesJson:
                        currentTypesList.append(PokepediaElementType.fromStr(typeJson['type']['name']))

            elementTypeGenerationDictionary[pokepediaGeneration] = currentTypesList

        # only store typing for generations where this Pokemon actually existed
        for pokepediaGeneration in PokepediaGeneration:
            if pokepediaGeneration.value < initialGeneration.value:
                del elementTypeGenerationDictionary[pokepediaGeneration]

        # remove duplicates
        currentTypesList: List[PokepediaElementType] = None
        for pokepediaGeneration in PokepediaGeneration:
            if pokepediaGeneration in elementTypeGenerationDictionary:
                if currentTypesList is None:
                    currentTypesList = elementTypeGenerationDictionary[pokepediaGeneration]
                elif currentTypesList == elementTypeGenerationDictionary[pokepediaGeneration]:
                    del elementTypeGenerationDictionary[pokepediaGeneration]
                else:
                    currentTypesList = elementTypeGenerationDictionary[pokepediaGeneration]

        return elementTypeGenerationDictionary

    def __getEnDescription(self, jsonResponse: Dict) -> str:
        if not utils.hasItems(jsonResponse):
            raise ValueError(f'jsonResponse argument is malformed: \"{jsonResponse}\"')

        flavorTextEntries = jsonResponse.get('flavor_text_entries')
        if not utils.hasItems(flavorTextEntries):
            raise ValueError(f'\"flavor_text_entries\" field in JSON response is null or empty: {jsonResponse}')

        for flavorTextEntry in flavorTextEntries:
            if flavorTextEntry['language']['name'] == 'en':
                return utils.getStrFromDict(flavorTextEntry, 'flavor_text', clean = True)

        raise RuntimeError(f'can\'t find \"en\" language name in \"flavor_text_entries\" field: {jsonResponse}')

    def __getEnName(self, jsonResponse: Dict) -> str:
        if not utils.hasItems(jsonResponse):
            raise ValueError(f'jsonResponse argument is malformed: \"{jsonResponse}\"')

        names = jsonResponse.get('names')
        if not utils.hasItems(names):
            raise ValueError(f'\"names\" field in JSON response is null or empty: {jsonResponse}')

        for name in names:
            if name['language']['name'] == 'en':
                return utils.getStrFromDict(name, 'name', clean = True).title()

        raise RuntimeError(f'can\'t find \"en\" language name in \"names\" field: {jsonResponse}')

    def __getMoveGenerationDictionary(self, jsonResponse: Dict) -> Dict[PokepediaGeneration, PokepediaMoveGeneration]:
        if not utils.hasItems(jsonResponse):
            raise ValueError(f'jsonResponse argument is malformed: \"{jsonResponse}\"')

        # begin with current generation stats
        accuracy = jsonResponse['accuracy']
        power = jsonResponse['power']
        pp = utils.getIntFromDict(jsonResponse, 'pp')
        damageClass = PokepediaDamageClass.fromStr(jsonResponse['damage_class']['name'])
        elementType = PokepediaElementType.fromStr(jsonResponse['type']['name'])
        move = None

        pastValuesJson = jsonResponse.get('past_values')
        if pastValuesJson is None:
            raise ValueError(f'\"past_values\" field in JSON response is null: {jsonResponse}')

        moveGenerationDictionary: Dict[PokepediaGeneration, PokepediaMoveGeneration] = dict()

        # iterate backwards and insert into dictionary once a generation is found.
        # then 'un-patch' for previous generations.
        for pokepediaGeneration in reversed(PokepediaGeneration):
            for pastValueJson in pastValuesJson:
                generation = PokepediaGeneration.fromStr(pastValueJson['version_group']['name'])

                if generation == pokepediaGeneration:
                    if generation.isEarlyGeneration() and damageClass is not PokepediaDamageClass.STATUS:
                        damageClass = PokepediaDamageClass.getTypeBasedDamageClass(elementType)

                    moveGenerationDictionary[generation] = PokepediaMoveGeneration(
                        accuracy = accuracy,
                        power = power,
                        pp = pp,
                        damageClass = damageClass,
                        elementType = elementType,
                        generation = generation
                    )

                    if utils.isValidNum(pastValueJson.get('accuracy')):
                        accuracy = utils.getIntFromDict(pastValueJson, 'accuracy')

                    if utils.isValidNum(pastValueJson.get('power')):
                        power = utils.getIntFromDict(pastValueJson, 'power')

                    if utils.isValidNum(pastValueJson.get('pp')):
                        pp = utils.getIntFromDict(pastValueJson, 'pp')

                    if pastValueJson.get('type') is not None:
                        elementType = PokepediaElementType.fromStr(pastValueJson['type']['name'])

        generation = PokepediaGeneration.fromStr(jsonResponse['generation']['name'])

        if generation.isEarlyGeneration() and  damageClass is not PokepediaDamageClass.STATUS:
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
        print(f'Searching PokeAPI for move \"{name}\"...')

        rawResponse = None
        try:
            rawResponse = requests.get(
                url = f'https://pokeapi.co/api/v2/move/{name}/',
                timeout = utils.getDefaultTimeout()
            )
        except (ConnectionError, HTTPError, MaxRetryError, NewConnectionError, ReadTimeout, Timeout, TooManyRedirects) as e:
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
            rawName = utils.getStrFromDict(jsonResponse, 'name')
        )

    def searchPokemon(self, name: str) -> PokepediaPokemon:
        if not utils.isValidStr(name):
            raise ValueError(f'name argument is malformed: \"{name}\"')

        name = utils.cleanStr(name)
        name = name.replace(' ', '-')
        print(f'Searching PokeAPI for Pokemon \"{name}\"...')

        rawResponse = None
        try:
            rawResponse = requests.get(
                url = f'https://pokeapi.co/api/v2/pokemon/{name}/',
                timeout = utils.getDefaultTimeout()
            )
        except (ConnectionError, HTTPError, MaxRetryError, NewConnectionError, ReadTimeout, Timeout, TooManyRedirects) as e:
            print(f'Exception occurred when attempting to fetch Pokemon \"{name}\": {e}')
            raise RuntimeError(f'Exception occurred when attempting to fetch Pokemon \"{name}\": {e}')

        jsonResponse = None
        try:
            jsonResponse = rawResponse.json()
        except JSONDecodeError as e:
            print(f'Exception occurred when attempting to decode Pokemon response into JSON for \"{name}\": {e}')
            raise RuntimeError(f'Exception occurred when attempting to decode Pokemon response into JSON for \"{name}\": {e}')

        pokedexId = utils.getIntFromDict(jsonResponse, 'id')
        initialGeneration = PokepediaGeneration.fromPokedexId(pokedexId)

        return PokepediaPokemon(
            generationElementTypes = self.__getElementTypeGenerationDictionary(
                jsonResponse = jsonResponse,
                initialGeneration = initialGeneration
            ),
            initialGeneration = initialGeneration,
            height = utils.getIntFromDict(jsonResponse, 'height'),
            pokedexId = pokedexId,
            weight = utils.getIntFromDict(jsonResponse, 'weight'),
            name = utils.getStrFromDict(jsonResponse, 'name').title()
        )

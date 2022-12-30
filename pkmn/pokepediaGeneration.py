from enum import Enum, auto

try:
    import CynanBotCommon.utils as utils
except:
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
    def fromPokedexId(cls, pokedexId: int):
        if not utils.isValidNum(pokedexId):
            raise ValueError(f'pokedexId argument is malformed: \"{pokedexId}\"')
        elif pokedexId < 0:
            raise ValueError(f'pokedexId argument is out of bounds: \"{pokedexId}\"')

        if pokedexId <= PokepediaGeneration.GENERATION_1.getMaxPokedexId():
            return PokepediaGeneration.GENERATION_1
        elif pokedexId <= PokepediaGeneration.GENERATION_2.getMaxPokedexId():
            return PokepediaGeneration.GENERATION_2
        elif pokedexId <= PokepediaGeneration.GENERATION_3.getMaxPokedexId():
            return PokepediaGeneration.GENERATION_3
        elif pokedexId <= PokepediaGeneration.GENERATION_4.getMaxPokedexId():
            return PokepediaGeneration.GENERATION_4
        elif pokedexId <= PokepediaGeneration.GENERATION_5.getMaxPokedexId():
            return PokepediaGeneration.GENERATION_5
        elif pokedexId <= PokepediaGeneration.GENERATION_6.getMaxPokedexId():
            return PokepediaGeneration.GENERATION_6
        elif pokedexId <= PokepediaGeneration.GENERATION_7.getMaxPokedexId():
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

    def getMaxPokedexId(self) -> int:
        if self is PokepediaGeneration.GENERATION_1:
            return 151
        elif self is PokepediaGeneration.GENERATION_2:
            return 251
        elif self is PokepediaGeneration.GENERATION_3:
            return 386
        elif self is PokepediaGeneration.GENERATION_4:
            return 493
        elif self is PokepediaGeneration.GENERATION_5:
            return 649
        elif self is PokepediaGeneration.GENERATION_6:
            return 721
        elif self is PokepediaGeneration.GENERATION_7:
            return 809
        elif self is PokepediaGeneration.GENERATION_8:
            return 905
        else:
            raise RuntimeError(f'unknown PokepediaGeneration: \"{self}\"')

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

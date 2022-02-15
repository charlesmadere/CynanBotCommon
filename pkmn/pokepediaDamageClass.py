from enum import Enum, auto

try:
    import CynanBotCommon.utils as utils
    from CynanBotCommon.pkmn.pokepediaElementType import PokepediaElementType
except:
    import utils

    from pkmn.pokepediaElementType import PokepediaElementType


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

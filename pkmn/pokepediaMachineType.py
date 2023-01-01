import re
from enum import Enum, auto

try:
    import CynanBotCommon.utils as utils
except:
    import utils


class PokepediaMachineType(Enum):

    HM = auto()
    TM = auto()
    TR = auto()

    @classmethod
    def fromStr(cls, text: str):
        if not utils.isValidStr(text):
            raise ValueError(f'text argument is malformed: \"{text}\"')

        text = text.lower()

        if text.startswith('hm'):
            return PokepediaMachineType.HM
        elif text.startswith('tm'):
            return PokepediaMachineType.TM
        elif text.startswith('tr'):
            return PokepediaMachineType.TR
        else:
            raise ValueError(f'unknown PokepediaMachineType: \"{text}\"')

    def getPrefix(self) -> str:
        if self is PokepediaMachineType.HM:
            return 'HM'
        elif self is PokepediaMachineType.TM:
            return 'TM'
        elif self is PokepediaMachineType.TR:
            return 'TR'
        else:
            raise RuntimeError(f'unknown PokepediaMachineType: \"{self}\"')

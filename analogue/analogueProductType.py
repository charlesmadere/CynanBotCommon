from enum import Enum, auto

try:
    import CynanBotCommon.utils as utils
except:
    import utils


class AnalogueProductType(Enum):

    DAC = auto()
    DUO = auto()
    MEGA_SG = auto()
    NT_MINI = auto()
    OTHER = auto()
    POCKET = auto()
    SUPER_NT = auto()

    @classmethod
    def fromStr(cls, text: str):
        if not utils.isValidStr(text):
            return AnalogueProductType.OTHER

        text = text.lower()

        if 'dac' in text or 'dac' == text:
            return AnalogueProductType.DAC
        elif 'duo' in text or 'duo' == text:
            return AnalogueProductType.DUO
        elif 'mega sg -' in text or 'mega sg' == text:
            return AnalogueProductType.MEGA_SG
        elif 'nt mini' in text or 'nt mini' == text:
            return AnalogueProductType.NT_MINI
        elif 'pocket -' in text or 'pocket' == text:
            return AnalogueProductType.POCKET
        elif 'super nt -' in text or 'super nt' == text:
            return AnalogueProductType.SUPER_NT
        else:
            return AnalogueProductType.OTHER

    def toStr(self) -> str:
        if self is AnalogueProductType.DAC:
            return 'DAC'
        elif self is AnalogueProductType.DUO:
            return 'Duo'
        elif self is AnalogueProductType.MEGA_SG:
            return 'Mega Sg'
        elif self is AnalogueProductType.NT_MINI:
            return 'Nt mini'
        elif self is AnalogueProductType.OTHER:
            return 'other'
        elif self is AnalogueProductType.POCKET:
            return 'Pocket'
        elif self is AnalogueProductType.SUPER_NT:
            return 'Super Nt'
        else:
            raise RuntimeError(f'unknown AnalogueProductType: \"{self}\"')

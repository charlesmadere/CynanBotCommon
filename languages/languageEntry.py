from typing import List

try:
    import CynanBotCommon.utils as utils
except:
    import utils


class LanguageEntry():

    def __init__(
        self,
        commandNames: List[str],
        name: str,
        flag: str = None,
        iso6391Code: str = None,
        wotdApiCode: str = None
    ):
        if not utils.hasItems(commandNames):
            raise ValueError(f'commandNames argument is malformed: \"{commandNames}\"')
        elif not utils.isValidStr(name):
            raise ValueError(f'name argument is malformed: \"{name}\"')

        self.__commandNames: List[str] = commandNames
        self.__name: str = name
        self.__flag: str = flag
        self.__iso6391Code: str = iso6391Code
        self.__wotdApiCode: str = wotdApiCode

    def getCommandNames(self) -> List[str]:
        return self.__commandNames

    def getFlag(self) -> str:
        return self.__flag

    def getIso6391Code(self) -> str:
        if self.hasIso6391Code():
            return self.__iso6391Code
        else:
            raise RuntimeError(f'this LanguageEntry ({self.getName()}) has no ISO 639-1 code!')

    def getName(self) -> str:
        return self.__name

    def getPrimaryCommandName(self) -> str:
        return self.__commandNames[0]

    def getWotdApiCode(self) -> str:
        if self.hasWotdApiCode():
            return self.__wotdApiCode
        else:
            raise RuntimeError(f'this LanguageEntry ({self.getName()}) has no Word Of The Day API code!')

    def hasFlag(self) -> bool:
        return utils.isValidStr(self.__flag)

    def hasIso6391Code(self) -> bool:
        return utils.isValidStr(self.__iso6391Code)

    def hasWotdApiCode(self) -> bool:
        return utils.isValidStr(self.__wotdApiCode)

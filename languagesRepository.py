import random
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


class LanguagesRepository():

    def __init__(self):
        self.__languageList: List[LanguageEntry] = self.__createLanguageList()

    def __createLanguageList(self) -> List[LanguageEntry]:
        languages = list()

        languages.append(LanguageEntry(
            commandNames = [ 'de', 'deutsche', 'german', 'germany' ],
            flag = '🇩🇪',
            iso6391Code = 'de',
            name = 'German',
            wotdApiCode = 'de'
        ))

        languages.append(LanguageEntry(
            commandNames = [ 'en', 'eng', 'english', '英語' ],
            flag = '🇬🇧',
            iso6391Code = 'en',
            name = 'English'
        ))

        languages.append(LanguageEntry(
            commandNames = [ 'en-es' ],
            name = 'English for Spanish speakers',
            wotdApiCode = 'en-es'
        ))

        languages.append(LanguageEntry(
            commandNames = [ 'en-pt' ],
            name = 'English for Portuguese speakers',
            wotdApiCode = 'en-pt'
        ))

        languages.append(LanguageEntry(
            commandNames = [ 'es', 'español', 'sp', 'spanish' ],
            iso6391Code = 'es',
            name = 'Spanish',
            wotdApiCode = 'es'
        ))

        languages.append(LanguageEntry(
            commandNames = [ 'fr', 'français', 'france', 'french' ],
            flag = '🇫🇷',
            iso6391Code = 'fr',
            name = 'French',
            wotdApiCode = 'fr'
        ))

        languages.append(LanguageEntry(
            commandNames = [ 'el', 'greek' ],
            flag = '🇬🇷',
            iso6391Code = 'el',
            name = 'Greek'
        ))

        languages.append(LanguageEntry(
            commandNames = [ 'it', 'italian', 'italiano', 'italy' ],
            flag = '🇮🇹',
            iso6391Code = 'it',
            name = 'Italian',
            wotdApiCode = 'it'
        ))

        languages.append(LanguageEntry(
            commandNames = [ 'ja', 'japan', 'japanese', 'jp', '日本語', 'にほんご' ],
            flag = '🇯🇵',
            iso6391Code = 'ja',
            name = 'Japanese',
            wotdApiCode = 'ja'
        ))

        languages.append(LanguageEntry(
            commandNames = [ 'ko', 'korea', 'korean', '한국어' ],
            flag = '🇰🇷',
            iso6391Code = 'ko',
            name = 'Korean',
            wotdApiCode = 'korean'
        ))

        languages.append(LanguageEntry(
            commandNames = [ 'la', 'latin' ],
            iso6391Code = 'la',
            name = 'Latin'
        ))

        languages.append(LanguageEntry(
            commandNames = [ 'nl', 'dutch', 'nederlands', 'netherlands', 'vlaams' ],
            flag = '🇳🇱',
            iso6391Code = 'nl',
            name = 'Dutch',
            wotdApiCode = 'nl'
        ))

        languages.append(LanguageEntry(
            commandNames = [ 'no', 'norsk', 'norway', 'norwegian' ],
            flag = '🇳🇴',
            iso6391Code = 'no',
            name = 'Norwegian',
            wotdApiCode = 'norwegian'
        ))

        languages.append(LanguageEntry(
            commandNames = [ 'po', 'poland', 'polish' ],
            flag = '🇵🇱',
            iso6391Code = 'pl',
            name = 'Polish',
            wotdApiCode = 'polish',
        ))

        languages.append(LanguageEntry(
            commandNames = [ 'pt', 'portuguese', 'português' ],
            flag = '🇧🇷',
            iso6391Code = 'pt',
            name = 'Portuguese',
            wotdApiCode = 'pt'
        ))

        languages.append(LanguageEntry(
            commandNames = [ 'ru', 'russia', 'russian', 'русский' ],
            flag = '🇷🇺',
            iso6391Code = 'ru',
            name = 'Russian',
            wotdApiCode = 'ru'
        ))

        languages.append(LanguageEntry(
            commandNames = [ 'se', 'sv', 'svenska', 'sw', 'sweden', 'swedish' ],
            flag = '🇸🇪',
            iso6391Code = 'sv',
            name = 'Swedish',
            wotdApiCode = 'swedish',
        ))

        languages.append(LanguageEntry(
            commandNames = [ 'th', 'thai' ],
            flag = '🇹🇭',
            iso6391Code = 'th',
            name = 'Thai'
        ))

        languages.append(LanguageEntry(
            commandNames = [ 'zh', 'chinese', 'china', '中文' ],
            flag = '🇨🇳',
            iso6391Code = 'zh',
            name = 'Chinese',
            wotdApiCode = 'zh'
        ))

        return languages

    def getAllWotdApiCodes(self, delimiter: str = ', ') -> str:
        if delimiter is None:
            raise ValueError(f'delimiter argument is malformed: \"{delimiter}\"')

        wotdApiCodes = list()
        validEntries = self.__getLanguageEntries(hasWotdApiCode = True)
        for entry in validEntries:
            wotdApiCodes.append(entry.getWotdApiCode())

        wotdApiCodes.sort()
        return delimiter.join(wotdApiCodes)

    def getExampleLanguageEntry(
        self,
        hasIso6391Code: bool = None,
        hasWotdApiCode: bool = None
    ) -> LanguageEntry:
        validEntries = self.__getLanguageEntries(hasIso6391Code, hasWotdApiCode)
        return random.choice(validEntries)

    def __getLanguageEntries(
        self,
        hasIso6391Code: bool = None,
        hasWotdApiCode: bool = None
    ) -> List[LanguageEntry]:
        if hasIso6391Code is not None and not utils.isValidBool(hasIso6391Code):
            raise ValueError(f'hasIso6391Code argument is malformed: \"{hasIso6391Code}\"')
        elif hasWotdApiCode is not None and not utils.isValidBool(hasWotdApiCode):
            raise ValueError(f'hasWotdApiCode argument is malformed: \"{hasWotdApiCode}\"')

        validEntries: List[LanguageEntry] = list()

        for entry in self.__languageList:
            if hasIso6391Code is not None and hasWotdApiCode is not None:
                if hasIso6391Code == entry.hasIso6391Code() and hasWotdApiCode == entry.hasWotdApiCode():
                    validEntries.append(entry)
            elif hasIso6391Code is not None:
                if hasIso6391Code == entry.hasIso6391Code():
                    validEntries.append(entry)
            elif hasWotdApiCode is not None:
                if hasWotdApiCode == entry.hasWotdApiCode():
                    validEntries.append(entry)
            else:
                validEntries.append(entry)

        if not utils.hasItems(validEntries):
            raise RuntimeError(f'Unable to find a single LanguageEntry with arguments hasIso6391Code:{hasIso6391Code} and hasWotdApiCode:{hasWotdApiCode}')

        return validEntries

    def getLanguageForCommand(
        self,
        command: str,
        hasIso6391Code: bool = None,
        hasWotdApiCode: bool = None
    ) -> LanguageEntry:
        if not utils.isValidStr(command):
            raise ValueError(f'command argument is malformed: \"{command}\"')

        validEntries = self.__getLanguageEntries(hasIso6391Code, hasWotdApiCode)

        for entry in validEntries:
            for entryCommandName in entry.getCommandNames():
                if entryCommandName.lower() == command.lower():
                    return entry

        return None

    def requireLanguageForCommand(
        self,
        command: str,
        hasIso6391Code: bool = None,
        hasWotdApiCode: bool = None
    ) -> LanguageEntry:
        languageEntry = self.getLanguageForCommand(command, hasIso6391Code, hasWotdApiCode)

        if languageEntry is None:
            raise RuntimeError(f'Unable to find LanguageEntry for \"{command}\"')

        return languageEntry

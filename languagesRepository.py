import random
from typing import List

try:
    import CynanBotCommon.utils as utils
except:
    import utils


class LanguageEntry():

    def __init__(
        self,
        isEnabledForWotd: bool,
        commandNames: List[str],
        apiName: str,
        name: str,
        flag: str = None
    ):
        if not utils.isValidBool(isEnabledForWotd):
            raise ValueError(f'isEnabledForWotd argument is malformed: \"{isEnabledForWotd}\"')
        elif not utils.hasItems(commandNames):
            raise ValueError(f'commandNames argument is malformed: \"{commandNames}\"')
        elif not utils.isValidStr(apiName):
            raise ValueError(f'apiName argument is malformed: \"{apiName}\"')
        elif not utils.isValidStr(name):
            raise ValueError(f'name argument is malformed: \"{name}\"')

        self.__isEnabledForWotd: bool = isEnabledForWotd
        self.__commandNames: List[str] = commandNames
        self.__apiName: str = apiName
        self.__name: str = name
        self.__flag: str = flag

    def getApiName(self) -> str:
        return self.__apiName

    def getCommandNames(self) -> List[str]:
        return self.__commandNames

    def getFlag(self) -> str:
        return self.__flag

    def getName(self) -> str:
        return self.__name

    def getPrimaryCommandName(self) -> str:
        return self.__commandNames[0]

    def hasFlag(self) -> bool:
        return utils.isValidStr(self.__flag)

    def isEnabledForWotd(self) -> bool:
        return self.__isEnabledForWotd


class LanguagesRepository():

    def __init__(self):
        self.__languageList: List[LanguageEntry] = self.__createLanguageList()

    def __createLanguageList(self) -> List[LanguageEntry]:
        languages = list()

        languages.append(LanguageEntry(
            isEnabledForWotd = True,
            apiName = 'de',
            commandNames = [ 'de', 'german', 'germany' ],
            flag = '🇩🇪',
            name = 'German'
        ))

        languages.append(LanguageEntry(
            isEnabledForWotd = True,
            apiName = 'en-es',
            commandNames = [ 'en-es' ],
            name = 'English for Spanish speakers'
        ))

        languages.append(LanguageEntry(
            isEnabledForWotd = True,
            apiName = 'en-pt',
            commandNames = [ 'en-pt' ],
            name = 'English for Portuguese speakers'
        ))

        languages.append(LanguageEntry(
            isEnabledForWotd = True,
            apiName = 'es',
            commandNames = [ 'es', 'spanish' ],
            name = 'Spanish'
        ))

        languages.append(LanguageEntry(
            isEnabledForWotd = True,
            apiName = 'fr',
            commandNames = [ 'fr', 'france', 'french' ],
            flag = '🇫🇷',
            name = 'French'
        ))

        languages.append(LanguageEntry(
            isEnabledForWotd = True,
            apiName = 'it',
            commandNames = [ 'it', 'italian', 'italy' ],
            flag = '🇮🇹',
            name = 'Italian'
        ))

        languages.append(LanguageEntry(
            isEnabledForWotd = True,
            apiName = 'ja',
            commandNames = [ 'ja', 'jp', 'japan', 'japanese' ],
            flag = '🇯🇵',
            name = 'Japanese'
        ))

        languages.append(LanguageEntry(
            isEnabledForWotd = True,
            apiName = 'korean',
            commandNames = [ 'ko', 'korea', 'korean' ],
            flag = '🇰🇷',
            name = 'Korean'
        ))

        languages.append(LanguageEntry(
            isEnabledForWotd = True,
            apiName = 'nl',
            commandNames = [ 'nl', 'dutch', 'netherlands' ],
            flag = '🇳🇱',
            name = 'Dutch'
        ))

        languages.append(LanguageEntry(
            isEnabledForWotd = True,
            apiName = 'norwegian',
            commandNames = [ 'no', 'norway', 'norwegian' ],
            flag = '🇳🇴',
            name = 'Norwegian'
        ))

        languages.append(LanguageEntry(
            isEnabledForWotd = True,
            apiName = 'polish',
            commandNames = [ 'po', 'poland', 'polish' ],
            flag = '🇵🇱',
            name = 'Polish'
        ))

        languages.append(LanguageEntry(
            isEnabledForWotd = True,
            apiName = 'pt',
            commandNames = [ 'pt', 'portuguese' ],
            flag = '🇧🇷',
            name = 'Portuguese'
        ))

        languages.append(LanguageEntry(
            isEnabledForWotd = True,
            apiName = 'ru',
            commandNames = [ 'ru', 'russia', 'russian' ],
            flag = '🇷🇺',
            name = 'Russian'
        ))

        languages.append(LanguageEntry(
            isEnabledForWotd = True,
            apiName = 'swedish',
            commandNames = [ 'sv', 'se', 'sw', 'sweden', 'swedish' ],
            flag = '🇸🇪',
            name = 'Swedish'
        ))

        languages.append(LanguageEntry(
            isEnabledForWotd = True,
            apiName = 'zh',
            commandNames = [ 'zh', 'chinese', 'china' ],
            flag = '🇨🇳',
            name = 'Chinese'
        ))

        return languages

    def getAllApiNames(self, delimiter: str = ', ') -> str:
        if delimiter is None:
            raise ValueError(f'delimiter argument is malformed: \"{delimiter}\"')

        apiNames = list()
        for entry in self.__languageList:
            apiNames.append(entry.getApiName())

        apiNames.sort()
        return delimiter.join(apiNames)

    def getAllCommandNames(self, delimiter: str = ', ') -> str:
        if delimiter is None:
            raise ValueError(f'delimiter argument is malformed: \"{delimiter}\"')

        commandNames = list()
        for entry in self.__languageList:
            commandNames.append(entry.getPrimaryCommandName())

        commandNames.sort()
        return delimiter.join(commandNames)

    def getExampleLanguageEntry(self) -> LanguageEntry:
        return random.choice(self.__languageList)

    def getLanguageForCommand(self, command: str) -> LanguageEntry:
        if not utils.isValidStr(command):
            raise ValueError(f'command argument is malformed: \"{command}\"')

        for entry in self.__languageList:
            for commandName in entry.getCommandNames():
                if commandName.lower() == command.lower():
                    return entry

        return None

    def requireLanguageForCommand(self, command: str) -> LanguageEntry:
        if not utils.isValidStr(command):
            raise ValueError(f'command argument is malformed: \"{command}\"')

        languageEntry = self.getLanguageForCommand(command)

        if languageEntry is None:
            raise RuntimeError(f'Unable to find LanguageEntry for \"{command}\"')

        return languageEntry

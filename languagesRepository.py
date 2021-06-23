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
        apiName: str,
        flag: str = None
    ):
        if not utils.hasItems(commandNames):
            raise ValueError(f'commandNames argument is malformed: \"{commandNames}\"')
        elif not utils.isValidStr(apiName):
            raise ValueError(f'apiName argument is malformed: \"{apiName}\"')

        self.__commandNames: List[str] = commandNames
        self.__apiName: str = apiName
        self.__flag: str = flag

    def getApiName(self) -> str:
        return self.__apiName

    def getCommandNames(self) -> List[str]:
        return self.__commandNames

    def getFlag(self) -> str:
        return self.__flag

    def getPrimaryCommandName(self) -> str:
        return self.__commandNames[0]

    def hasFlag(self) -> bool:
        return utils.isValidStr(self.__flag)

class LanguagesRepository():

    def __init__(self):
        self.__languageList: List[LanguageEntry] = self.__createLanguageList()

    def __createLanguageList(self) -> List[LanguageEntry]:
        languages = list()

        languages.append(LanguageEntry(
            apiName = 'de',
            commandNames = [ 'de', 'german', 'germany' ],
            flag = '🇩🇪'
        ))

        languages.append(LanguageEntry(
            apiName = 'en-es',
            commandNames = [ 'en-es' ]
        ))

        languages.append(LanguageEntry(
            apiName = 'en-pt',
            commandNames = [ 'en-pt' ]
        ))

        languages.append(LanguageEntry(
            apiName = 'es',
            commandNames = [ 'es', 'spanish' ]
        ))

        languages.append(LanguageEntry(
            apiName = 'fr',
            commandNames = [ 'fr', 'france', 'french' ],
            flag = '🇫🇷'
        ))

        languages.append(LanguageEntry(
            apiName = 'it',
            commandNames = [ 'it', 'italian', 'italy' ],
            flag = '🇮🇹'
        ))

        languages.append(LanguageEntry(
            apiName = 'ja',
            commandNames = [ 'ja', 'jp', 'japan', 'japanese' ],
            flag = '🇯🇵'
        ))

        languages.append(LanguageEntry(
            apiName = 'korean',
            commandNames = [ 'ko', 'korea', 'korean' ],
            flag = '🇰🇷'
        ))

        languages.append(LanguageEntry(
            apiName = 'nl',
            commandNames = [ 'nl', 'dutch', 'netherlands' ],
            flag = '🇳🇱'
        ))

        languages.append(LanguageEntry(
            apiName = 'norwegian',
            commandNames = [ 'no', 'norway', 'norwegian' ],
            flag = '🇳🇴'
        ))

        languages.append(LanguageEntry(
            apiName = 'polish',
            commandNames = [ 'po', 'poland', 'polish' ],
            flag = '🇵🇱'
        ))

        languages.append(LanguageEntry(
            apiName = 'pt',
            commandNames = [ 'pt', 'portuguese' ],
            flag = '🇧🇷'
        ))

        languages.append(LanguageEntry(
            apiName = 'ru',
            commandNames = [ 'ru', 'russia', 'russian' ],
            flag = '🇷🇺'
        ))

        languages.append(LanguageEntry(
            apiName = 'swedish',
            commandNames = [ 'sv', 'se', 'sw', 'sweden', 'swedish' ],
            flag = '🇸🇪'
        ))

        languages.append(LanguageEntry(
            apiName = 'zh',
            commandNames = [ 'zh', 'chinese', 'china' ],
            flag = '🇨🇳'
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

        raise RuntimeError(f'Unable to find language for \"{command}\"')

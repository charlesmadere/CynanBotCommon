try:
    import CynanBotCommon.utils as utils
    from CynanBotCommon.language.languageEntry import LanguageEntry
except:
    import utils
    from language.languageEntry import LanguageEntry


class WordOfTheDayResponse():

    def __init__(
        self,
        languageEntry: LanguageEntry,
        definition: str,
        englishExample: str,
        foreignExample: str,
        transliteration: str,
        word: str
    ):
        if not isinstance(languageEntry, LanguageEntry):
            raise ValueError(f'languageEntry argument is malformed: \"{languageEntry}\"')
        elif not utils.isValidStr(definition):
            raise ValueError(f'definition argument is malformed: \"{definition}\"')
        elif not utils.isValidStr(word):
            raise ValueError(f'word argument is malformed: \"{word}\"')

        self.__languageEntry: LanguageEntry = languageEntry
        self.__definition: str = definition
        self.__englishExample: str = englishExample
        self.__foreignExample: str = foreignExample
        self.__transliteration: str = transliteration
        self.__word: str = word

    def getDefinition(self) -> str:
        return self.__definition

    def getEnglishExample(self) -> str:
        return self.__englishExample

    def getForeignExample(self) -> str:
        return self.__foreignExample

    def getLanguageEntry(self) -> LanguageEntry:
        return self.__languageEntry

    def getLanguageName(self) -> str:
        return self.__languageEntry.getName()

    def getTransliteration(self) -> str:
        return self.__transliteration

    def getWord(self) -> str:
        return self.__word

    def hasExamples(self) -> bool:
        return utils.isValidStr(self.__englishExample) and utils.isValidStr(self.__foreignExample)

    def hasTransliteration(self) -> bool:
        return utils.isValidStr(self.__transliteration)

    def toStr(self) -> str:
        languageNameAndFlag = None
        if self.__languageEntry.hasFlag():
            languageNameAndFlag = f'{self.__languageEntry.getFlag()} {self.getLanguageName()}'
        else:
            languageNameAndFlag = self.getLanguageName()

        if self.hasExamples():
            if self.hasTransliteration():
                return f'{languageNameAndFlag} — {self.getWord()} ({self.getTransliteration()}) — {self.getDefinition()}. Example: {self.getForeignExample()} {self.getEnglishExample()}'
            else:
                return f'{languageNameAndFlag} — {self.getWord()} — {self.getDefinition()}. Example: {self.getForeignExample()} {self.getEnglishExample()}'
        elif self.hasTransliteration():
            return f'{languageNameAndFlag} — {self.getWord()} ({self.getTransliteration()}) — {self.getDefinition()}'
        else:
            return f'{languageNameAndFlag} — {self.getWord()} — {self.getDefinition()}'

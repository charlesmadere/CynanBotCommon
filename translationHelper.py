from os import path

from google.cloud import translate_v2 as translate

try:
    import CynanBotCommon.utils as utils
    from CynanBotCommon.languagesRepository import (LanguageEntry,
                                                    LanguagesRepository)
except:
    import utils
    from languagesRepository import LanguageEntry, LanguagesRepository


class TranslationResponse():

    def __init__(
        self,
        originalLanguage: LanguageEntry,
        translatedLanguage: LanguageEntry,
        originalText: str,
        translatedText: str
    ):
        if not utils.isValidStr(originalText):
            raise ValueError(f'originalText argument is malformed: \"{originalText}\"')
        elif not utils.isValidStr(translatedText):
            raise ValueError(f'translatedText argument is malformed: \"{translatedText}\"')

        self.__originalLanguage: LanguageEntry = originalLanguage
        self.__translatedLanguage: LanguageEntry = translatedLanguage
        self.__originalText: str = originalText
        self.__translatedText: str = translatedText

    def getOriginalLanguage(self) -> LanguageEntry:
        return self.__originalLanguage

    def getOriginalText(self) -> str:
        return self.__originalText

    def getTranslatedLanguage(self) -> LanguageEntry:
        return self.__translatedLanguage

    def getTranslatedText(self) -> str:
        return self.__translatedText

    def hasOriginalLanguage(self) -> bool:
        return self.__originalLanguage is not None

    def hasTranslatedLanguage(self) -> bool:
        return self.__translatedLanguage is not None

    def toStr(self) -> str:
        flagText = ''
        if self.hasOriginalLanguage() and self.__originalLanguage.hasFlag() and self.hasTranslatedLanguage() and self.__translatedLanguage.hasFlag():
            flagText = f'{self.__originalLanguage.getFlag()} ➡ {self.__translatedLanguage.getFlag()} — '

        return f'{flagText}{self.__translatedText}'


class TranslationHelper():

    def __init__(
        self,
        languagesRepository: LanguagesRepository,
        googleServiceAccountFile: str = 'CynanBotCommon/googleServiceAccount.json'
    ):
        if languagesRepository is None:
            raise ValueError(f'languagesRepository argument is malformed: \"{languagesRepository}\"')
        elif not utils.isValidStr(googleServiceAccountFile):
            raise ValueError(f'googleServiceAccountFile argument is malformed: \"{googleServiceAccountFile}\"')

        self.__languagesRepository: LanguagesRepository = languagesRepository
        self.__googleServiceAccountFile: str = googleServiceAccountFile
        self.__translateClient = None

    def __getTranslateClient(self):
        if self.__translateClient is None:
            print(f'Initializing new translate.Client instance... ({utils.getNowTimeText()})')

            if not path.exists(self.__googleServiceAccountFile):
                raise FileNotFoundError(f'googleServiceAccount file not found: \"{self.__googleServiceAccountFile}\"')

            self.__translateClient = translate.Client.from_service_account_json(self.__googleServiceAccountFile)

        return self.__translateClient

    def translate(
        self,
        text: str,
        targetLanguageEntry: LanguageEntry = None
    ) -> TranslationResponse:
        if not utils.isValidStr(text):
            raise ValueError(f'text argument is malformed: \"{text}\"')

        text = utils.cleanStr(text)

        if targetLanguageEntry is not None and not targetLanguageEntry.hasIso6391Code():
            raise ValueError(f'the given LanguageEntry is not supported for translation: \"{targetLanguageEntry.getName()}\"')
        elif targetLanguageEntry is None:
            targetLanguageEntry = self.__languagesRepository.requireLanguageForCommand(
                command = 'en',
                hasIso6391Code = True
            )

        translationResult = self.__getTranslateClient().translate(
            text,
            target_language = targetLanguageEntry.getIso6391Code()
        )

        if not utils.hasItems(translationResult):
            raise RuntimeError(f'error in the data response when attempting to translate \"{text}\": {translationResult}')

        originalText = translationResult.get('input')
        if not utils.isValidStr(originalText):
            raise RuntimeError(f'\"input\" field is missing or malformed from translation result for \"{text}\": {translationResult}')

        translatedText = translationResult.get('translatedText')
        if not utils.isValidStr(translatedText):
            raise RuntimeError(f'\"translatedText\" field is missing or malformed from translation result for \"{text}\": {translationResult}')

        originalLanguage: LanguageEntry = None
        detectedSourceLanguage = translationResult.get('detectedSourceLanguage')
        if utils.isValidStr(detectedSourceLanguage):
            originalLanguage = self.__languagesRepository.getLanguageForCommand(detectedSourceLanguage)

        return TranslationResponse(
            originalLanguage = originalLanguage,
            translatedLanguage = targetLanguageEntry,
            originalText = originalText,
            translatedText = translatedText
        )

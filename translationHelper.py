from google.cloud import translate_v2 as translate

try:
    import CynanBotCommon.utils as utils
    from CynanBotCommon.languagesRepository import LanguageEntry
except:
    import utils
    from languagesRepository import LanguageEntry


class TranslationHelper():

    def __init__(
        self,
        googleServiceAccountFile: str = 'googleServiceAccount.json'
    ):
        if not utils.isValidStr(googleServiceAccountFile):
            raise ValueError(f'googleServiceAccountFile argument is malformed: \"{googleServiceAccountFile}\"')

        self.__googleServiceAccountFile = googleServiceAccountFile
        self.__translateClient = None

    def __getTranslateClient(self):
        if self.__translateClient is None:
            self.__translateClient = translate.Client.from_service_account_json(self.__googleServiceAccountFile)

        return self.__translateClient

    def translate(self, text: str, targetLanguageEntry: LanguageEntry = None):
        if not utils.isValidStr(text):
            raise ValueError(f'text argument is malformed: \"{text}\"')

        targetLanguage = 'en'
        if targetLanguageEntry is not None:
            targetLanguage = targetLanguageEntry.getApiName()

        translationResult = self.__getTranslateClient().translate(
            text,
            target_language = targetLanguage
        )

        translatedText = translationResult.get('translatedText')
        if not utils.isValidStr(translatedText):
            raise RuntimeError(f'error when attempting to translate \"{text}\" into \"{targetLanguage}\" target language')

        return translatedText

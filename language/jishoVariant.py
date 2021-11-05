from typing import List

try:
    import CynanBotCommon.utils as utils
except:
    import utils


class JishoVariant():

    def __init__(
        self,
        definitions: List[str],
        partsOfSpeech: List[str],
        furigana: str,
        word: str
    ):
        if not utils.hasItems(definitions):
            raise ValueError(f'definitions argument is malformed: \"{definitions}\"')

        self.__definitions: List[str] = definitions
        self.__partsOfSpeech: List[str] = partsOfSpeech
        self.__furigana: str = furigana
        self.__word: str = word

    def getDefinitions(self) -> List[str]:
        return self.__definitions

    def getFurigana(self) -> str:
        return self.__furigana

    def getPartsOfSpeech(self) -> List[str]:
        return self.__partsOfSpeech

    def getWord(self) -> str:
        return self.__word

    def hasFurigana(self) -> bool:
        return utils.isValidStr(self.__furigana)

    def hasPartsOfSpeech(self) -> bool:
        return utils.hasItems(self.__partsOfSpeech)

    def hasWord(self) -> str:
        return self.__word

    def toStr(self, definitionDelimiter: str = ', ') -> str:
        if definitionDelimiter is None:
            raise ValueError(f'definitionDelimiter argument is malformed: \"{definitionDelimiter}\"')

        word = ''
        if self.hasWord():
            word = self.__word

        furigana = ''
        if self.hasFurigana():
            if utils.isValidStr(word):
                furigana = f' ({self.__furigana})'
            else:
                furigana = self.__furigana

        definitionsList: List[str] = list()
        for definition in self.__definitions:
            definitionsList.append(definition)

        definitions = definitionDelimiter.join(definitionsList)
        return f'{word}{furigana} — {definitions}'

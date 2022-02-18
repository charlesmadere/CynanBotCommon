from os import path
from typing import List

try:
    import CynanBotCommon.utils as utils
    from CynanBotCommon.trivia.absTriviaQuestion import AbsTriviaQuestion
    from CynanBotCommon.trivia.triviaContentCode import TriviaContentCode
except:
    import utils

    from trivia.absTriviaQuestion import AbsTriviaQuestion
    from trivia.triviaContentCode import TriviaContentCode


class TriviaContentScanner():

    def __init__(
        self,
        bannedWordsFile: str = 'CynanBotCommon/trivia/bannedWords.txt'
    ):
        if not utils.isValidStr(bannedWordsFile):
            raise ValueError(f'bannedWordsFile argument is malformed: \"{bannedWordsFile}\"')

        self.__bannedWordsFile: str = bannedWordsFile

    def __readBannedWords(self) -> List[str]:
        if not path.exists(self.__bannedWordsFile):
            raise FileNotFoundError(f'Banned Words file not found: \"{self.__bannedWordsFile}\"')

        with open(self.__bannedWordsFile, 'r') as file:
            lines = file.readlines()

        bannedWords: List[str] = list()

        if utils.hasItems(lines):
            for line in lines:
                if utils.isValidStr(line):
                    line = line.strip().lower()
                    bannedWords.append(line)

        if utils.hasItems(bannedWords):
            return bannedWords
        else:
            return None

    def verify(self, question: AbsTriviaQuestion) -> TriviaContentCode:
        if question is None:
            return TriviaContentCode.IS_NONE

        bannedWords = self.__readBannedWords()

        strings: List[str] = list()
        strings.append(question.getQuestion().lower())
        strings.append(question.getPrompt().lower())

        for response in question.getResponses():
            strings.append(response.lower())

        for string in strings:
            if not utils.isValidStr(string):
                return TriviaContentCode.CONTAINS_EMPTY_STR
            elif utils.containsUrl(string):
                return TriviaContentCode.CONTAINS_URL
            elif utils.hasItems(bannedWords):
                for bannedWord in bannedWords:
                    if bannedWord in string:
                        return TriviaContentCode.CONTAINS_BANNED_WORD

        return TriviaContentCode.OK

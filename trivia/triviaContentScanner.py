import re
from typing import Optional, Pattern, Set

try:
    import CynanBotCommon.utils as utils
    from CynanBotCommon.timber.timberInterface import TimberInterface
    from CynanBotCommon.trivia.absTriviaQuestion import AbsTriviaQuestion
    from CynanBotCommon.trivia.bannedWords.bannedPhrase import BannedPhrase
    from CynanBotCommon.trivia.bannedWords.bannedWord import BannedWord
    from CynanBotCommon.trivia.bannedWords.bannedWordsRepositoryInterface import \
        BannedWordsRepositoryInterface
    from CynanBotCommon.trivia.bannedWords.bannedWordType import BannedWordType
    from CynanBotCommon.trivia.triviaContentCode import TriviaContentCode
    from CynanBotCommon.trivia.triviaContentScannerInterface import \
        TriviaContentScannerInterface
    from CynanBotCommon.trivia.triviaSettingsRepositoryInterface import \
        TriviaSettingsRepositoryInterface
    from CynanBotCommon.trivia.triviaType import TriviaType
except:
    import utils
    from timber.timberInterface import TimberInterface
    from trivia.absTriviaQuestion import AbsTriviaQuestion
    from trivia.bannedWords.bannedPhrase import BannedPhrase
    from trivia.bannedWords.bannedWord import BannedWord
    from trivia.bannedWords.bannedWordsRepositoryInterface import \
        BannedWordsRepositoryInterface
    from trivia.bannedWords.bannedWordType import BannedWordType
    from trivia.triviaContentCode import TriviaContentCode
    from trivia.triviaContentScannerInterface import \
        TriviaContentScannerInterface
    from trivia.triviaSettingsRepositoryInterface import \
        TriviaSettingsRepositoryInterface
    from trivia.triviaType import TriviaType


class TriviaContentScanner(TriviaContentScannerInterface):

    def __init__(
        self,
        bannedWordsRepository: BannedWordsRepositoryInterface,
        timber: TimberInterface,
        triviaSettingsRepository: TriviaSettingsRepositoryInterface
    ):
        if not isinstance(bannedWordsRepository, BannedWordsRepositoryInterface):
            raise ValueError(f'bannedWordsRepository argument is malformed: \"{bannedWordsRepository}\"')
        elif not isinstance(timber, TimberInterface):
            raise ValueError(f'timber argument is malformed: \"{timber}\"')
        elif not isinstance(triviaSettingsRepository, TriviaSettingsRepositoryInterface):
            raise ValueError(f'triviaSettingsRepository argument is malformed: \"{triviaSettingsRepository}\"')

        self.__bannedWordsRepository: BannedWordsRepositoryInterface = bannedWordsRepository
        self.__timber: TimberInterface = timber
        self.__triviaSettingsRepository: TriviaSettingsRepositoryInterface = triviaSettingsRepository

        self.__phraseRegEx: Pattern = re.compile(r'[a-z]+', re.IGNORECASE)
        self.__wordRegEx: Pattern = re.compile(r'\w', re.IGNORECASE)

    async def __getAllPhrasesFromQuestion(self, question: AbsTriviaQuestion) -> Set[Optional[str]]:
        if not isinstance(question, AbsTriviaQuestion):
            raise ValueError(f'question argument is malformed: \"{question}\"')

        phrases: Set[Optional[str]] = set()
        await self.__updateQuestionPhrasesContent(phrases, question.getQuestion())
        await self.__updateQuestionPhrasesContent(phrases, question.getPrompt())

        if question.hasCategory():
            await self.__updateQuestionPhrasesContent(phrases, question.getCategory())

        for correctAnswer in question.getCorrectAnswers():
            await self.__updateQuestionPhrasesContent(phrases, correctAnswer)

        for response in question.getResponses():
            await self.__updateQuestionPhrasesContent(phrases, response)

        return phrases

    async def __getAllWordsFromQuestion(self, question: AbsTriviaQuestion) -> Set[Optional[str]]:
        if not isinstance(question, AbsTriviaQuestion):
            raise ValueError(f'question argument is malformed: \"{question}\"')

        words: Set[Optional[str]] = set()
        await self.__updateQuestionWordsContent(words, question.getQuestion())
        await self.__updateQuestionWordsContent(words, question.getPrompt())

        if question.hasCategory():
            await self.__updateQuestionWordsContent(words, question.getCategory())

        for correctAnswer in question.getCorrectAnswers():
            await self.__updateQuestionWordsContent(words, correctAnswer)

        for response in question.getResponses():
            await self.__updateQuestionWordsContent(words, response)

        return words

    async def __updateQuestionPhrasesContent(
        self,
        phrases: Set[str],
        string: Optional[str]
    ):
        if not isinstance(phrases, Set):
            raise ValueError(f'phrases argument is malformed: \"{phrases}\"')

        if not utils.isValidStr(string):
            return

        string = string.lower()
        words = self.__phraseRegEx.findall(string)

        if not utils.hasItems(words):
            return

        phrase = ' '.join(words)
        phrases.update(phrase)

    async def __updateQuestionWordsContent(
        self,
        words: Set[Optional[str]],
        string: Optional[str]
    ):
        if not isinstance(words, Set):
            raise ValueError(f'words argument is malformed: \"{words}\"')

        if not utils.isValidStr(string):
            return

        splits = string.lower().split()

        if not utils.hasItems(splits):
            return

        for split in splits:
            words.add(split)

            characters = self.__wordRegEx.findall(split)
            if not utils.hasItems(characters):
                continue

            word = ''.join(characters)
            words.update(word)

    async def verify(self, question: Optional[AbsTriviaQuestion]) -> TriviaContentCode:
        if question is not None and not isinstance(question, AbsTriviaQuestion):
            raise ValueError(f'question argument is malformed: \"{question}\"')

        if question is None:
            return TriviaContentCode.IS_NONE

        responsesContentCode = await self.__verifyQuestionResponseCount(question)
        if responsesContentCode is not TriviaContentCode.OK:
            return responsesContentCode

        lengthsContentCode = await self.__verifyQuestionContentLengths(question)
        if lengthsContentCode is not TriviaContentCode.OK:
            return lengthsContentCode

        words = await self.__getAllWordsFromQuestion(question)

        emptyStringsOrUrlsContentCode = await self.__verifyQuestionEmptyStringsOrUrls(words)
        if emptyStringsOrUrlsContentCode is not TriviaContentCode.OK:
            return emptyStringsOrUrlsContentCode

        phrases = await self.__getAllPhrasesFromQuestion(question)

        contentSanityCode = await self.__verifyQuestionContentProfanity(question, phrases, words)
        if contentSanityCode is not TriviaContentCode.OK:
            return contentSanityCode

        return TriviaContentCode.OK

    async def __verifyQuestionContentLengths(self, question: AbsTriviaQuestion) -> TriviaContentCode:
        maxQuestionLength = await self.__triviaSettingsRepository.getMaxQuestionLength()

        if len(question.getQuestion()) >= maxQuestionLength:
            self.__timber.log('TriviaContentScanner', f'Trivia question is too long (max is {maxQuestionLength}): {question.getQuestion()}')
            return TriviaContentCode.QUESTION_TOO_LONG

        maxPhraseAnswerLength = await self.__triviaSettingsRepository.getMaxPhraseAnswerLength()

        if question.getTriviaType() is TriviaType.QUESTION_ANSWER:
            for correctAnswer in question.getCorrectAnswers():
                if len(correctAnswer) >= maxPhraseAnswerLength:
                    self.__timber.log('TriviaContentScanner', f'Trivia answer is too long (max is {maxPhraseAnswerLength}): {question.getCorrectAnswers()}')
                    return TriviaContentCode.ANSWER_TOO_LONG

        maxAnswerLength = await self.__triviaSettingsRepository.getMaxAnswerLength()

        for response in question.getResponses():
            if len(response) >= maxAnswerLength:
                self.__timber.log('TriviaContentScanner', f'Trivia response is too long (max is {maxAnswerLength}): {question.getResponses()}')
                return TriviaContentCode.ANSWER_TOO_LONG

        return TriviaContentCode.OK

    async def __verifyQuestionContentProfanity(self,
        question: AbsTriviaQuestion,
        phrases: Set[str],
        words: Set[str]
    ) -> TriviaContentCode:
        if not isinstance(question, AbsTriviaQuestion):
            raise ValueError(f'question argument is malformed: \"{question}\"')
        elif not isinstance(phrases, Set):
            raise ValueError(f'phrases argument is malformed: \"{phrases}\"')
        elif not isinstance(words, Set):
            raise ValueError(f'words argument is malformed: \"{words}\"')

        absBannedWords = await self.__bannedWordsRepository.getBannedWordsAsync()

        for absBannedWord in absBannedWords:
            if absBannedWord.getType() is BannedWordType.EXACT_WORD:
                bannedWord: BannedWord = absBannedWord

                if bannedWord.getWord() in words:
                    self.__timber.log('TriviaContentScanner', f'Trivia content contains a banned word ({absBannedWord}): \"{bannedWord.getWord()}\"')
                    return TriviaContentCode.CONTAINS_BANNED_CONTENT
            elif absBannedWord.getType() is BannedWordType.PHRASE:
                bannedPhrase: BannedPhrase = absBannedWord

                for phrase in phrases:
                    if bannedPhrase.getPhrase() in phrase:
                        self.__timber.log('TriviaContentScanner', f'Trivia content contains a banned phrase ({absBannedWord}): \"{phrase}\"')
                        return TriviaContentCode.CONTAINS_BANNED_CONTENT
            else:
                raise RuntimeError(f'unknown BannedWordType ({absBannedWord}): \"{absBannedWord.getType()}\"')

        print(f'question: {question}, phrases: {phrases}, words: {words}, absBannedWords: {absBannedWord}')
        return TriviaContentCode.OK

    async def __verifyQuestionEmptyStringsOrUrls(self, words: Set[Optional[str]]):
        if not isinstance(words, Set):
            raise ValueError(f'words argument is malformed: \"{words}\"')

        for word in words:
            if not utils.isValidStr(word):
                self.__timber.log('TriviaContentScanner', f'Trivia content contains an empty string: \"{word}\"')
                return TriviaContentCode.CONTAINS_EMPTY_STR
            elif utils.containsUrl(word):
                self.__timber.log('TriviaContentScanner', f'Trivia content contains a URL: \"{word}\"')
                return TriviaContentCode.CONTAINS_URL

        return TriviaContentCode.OK

    async def __verifyQuestionResponseCount(self, question: AbsTriviaQuestion) -> TriviaContentCode:
        if question.getTriviaType() is not TriviaType.MULTIPLE_CHOICE:
            return TriviaContentCode.OK

        responses = question.getResponses()
        minMultipleChoiceResponses = await self.__triviaSettingsRepository.getMinMultipleChoiceResponses()

        if not utils.hasItems(responses) or len(responses) < minMultipleChoiceResponses:
            self.__timber.log('TriviaContentScanner', f'Trivia question has too few multiple choice responses (min is {minMultipleChoiceResponses}): {responses}')
            return TriviaContentCode.TOO_FEW_MULTIPLE_CHOICE_RESPONSES

        return TriviaContentCode.OK

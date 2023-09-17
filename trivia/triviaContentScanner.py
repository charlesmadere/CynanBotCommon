import re
from typing import Optional, Pattern, Set

try:
    import CynanBotCommon.utils as utils
    from CynanBotCommon.timber.timberInterface import TimberInterface
    from CynanBotCommon.trivia.absTriviaQuestion import AbsTriviaQuestion
    from CynanBotCommon.trivia.bannedWords.bannedWordCheckType import \
        BannedWordCheckType
    from CynanBotCommon.trivia.bannedWords.bannedWordsRepositoryInterface import \
        BannedWordsRepositoryInterface
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
    from trivia.bannedWords.bannedWordCheckType import BannedWordCheckType
    from trivia.bannedWords.bannedWordsRepositoryInterface import \
        BannedWordsRepositoryInterface
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

        self.__wordRegEx: Pattern = re.compile(r'\w', re.IGNORECASE)

    async def __updateQuestionStringContent(
        self,
        strings: Set[str],
        string: Optional[str]
    ):
        if not isinstance(strings, Set):
            raise ValueError(f'strings argument is malformed: \"{strings}\"')

        if not isinstance(string, str):
            return

        splits = string.lower().split()
        if not utils.hasItems(splits):
            return

        for split in splits:
            strings.add(split)

            characters = self.__wordRegEx.findall(split)
            if not utils.hasItems(characters):
                continue

            word = ''.join(characters)
            strings.update(word)

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

        contentSanityCode = await self.__verifyQuestionContentProfanity(question)
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

    async def __verifyQuestionContentProfanity(self, question: AbsTriviaQuestion) -> TriviaContentCode:
        strings: Set[str] = set()
        await self.__updateQuestionStringContent(strings, question.getQuestion())
        await self.__updateQuestionStringContent(strings, question.getPrompt())

        if question.hasCategory():
            await self.__updateQuestionStringContent(strings, question.getCategory())

        for correctAnswer in question.getCorrectAnswers():
            await self.__updateQuestionStringContent(strings, correctAnswer)

        for response in question.getResponses():
            await self.__updateQuestionStringContent(strings, response)

        bannedWords = await self.__bannedWordsRepository.getBannedWordsAsync()

        for string in strings:
            if not utils.isValidStr(string):
                self.__timber.log('TriviaContentScanner', f'Trivia content contains an empty string: \"{string}\"')
                return TriviaContentCode.CONTAINS_EMPTY_STR
            elif utils.containsUrl(string):
                self.__timber.log('TriviaContentScanner', f'Trivia content contains a URL: \"{string}\"')
                return TriviaContentCode.CONTAINS_URL

            for bannedWord in bannedWords:
                if bannedWord.getCheckType() is BannedWordCheckType.ANYWHERE:
                    if bannedWord.getWord() in string:
                        self.__timber.log('TriviaContentScanner', f'Trivia content contains a banned word ({bannedWord}): \"{string}\"')
                        return TriviaContentCode.CONTAINS_BANNED_WORD
                elif bannedWord.getCheckType() is BannedWordCheckType.EXACT_MATCH:
                    if bannedWord.getWord() == string:
                        self.__timber.log('TriviaContentScanner', f'Trivia content contains a banned word ({bannedWord}): \"{string}\"')
                        return TriviaContentCode.CONTAINS_BANNED_WORD
                else:
                    raise RuntimeError(f'unknown BannedWordTypeType ({bannedWord}): \"{bannedWord.getCheckType()}\"')

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

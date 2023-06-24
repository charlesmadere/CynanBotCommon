from typing import Optional, Set

try:
    import CynanBotCommon.utils as utils
    from CynanBotCommon.timber.timber import Timber
    from CynanBotCommon.trivia.absTriviaQuestion import AbsTriviaQuestion
    from CynanBotCommon.trivia.bannedWords.bannedWordCheckType import \
        BannedWordCheckType
    from CynanBotCommon.trivia.bannedWords.bannedWordsRepository import \
        BannedWordsRepository
    from CynanBotCommon.trivia.triviaContentCode import TriviaContentCode
    from CynanBotCommon.trivia.triviaSettingsRepository import \
        TriviaSettingsRepository
    from CynanBotCommon.trivia.triviaType import TriviaType
except:
    import utils
    from timber.timber import Timber
    from trivia.absTriviaQuestion import AbsTriviaQuestion
    from trivia.bannedWords.bannedWordCheckType import BannedWordCheckType
    from trivia.bannedWords.bannedWordsRepository import BannedWordsRepository
    from trivia.triviaContentCode import TriviaContentCode
    from trivia.triviaSettingsRepository import TriviaSettingsRepository
    from trivia.triviaType import TriviaType


class TriviaContentScanner():

    def __init__(
        self,
        bannedWordsRepository: BannedWordsRepository,
        timber: Timber,
        triviaSettingsRepository: TriviaSettingsRepository
    ):
        if not isinstance(bannedWordsRepository, BannedWordsRepository):
            raise ValueError(f'bannedWordsRepository argument is malformed: \"{bannedWordsRepository}\"')
        elif not isinstance(timber, Timber):
            raise ValueError(f'timber argument is malformed: \"{timber}\"')
        elif not isinstance(triviaSettingsRepository, TriviaSettingsRepository):
            raise ValueError(f'triviaSettingsRepository argument is malformed: \"{triviaSettingsRepository}\"')

        self.__bannedWordsRepository: BannedWordsRepository = bannedWordsRepository
        self.__timber: Timber = timber
        self.__triviaSettingsRepository: TriviaSettingsRepository = triviaSettingsRepository

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

        contentSanityCode = await self.__verifyQuestionContentSanity(question)
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

    async def __verifyQuestionContentSanity(self, question: AbsTriviaQuestion) -> TriviaContentCode:
        strings: Set[str] = set()
        strings.update(question.getQuestion().lower().split())
        strings.update(question.getPrompt().lower().split())

        if question.hasCategory():
            strings.update(question.getCategory().lower().split())

        for correctAnswer in question.getCorrectAnswers():
            strings.update(correctAnswer.lower().split())

        for response in question.getResponses():
            strings.update(response.lower().split())

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

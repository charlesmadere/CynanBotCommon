import math
import re
from typing import Any, Dict, Generator, List, Optional, Pattern

import polyleven

try:
    import CynanBotCommon.utils as utils
    from CynanBotCommon.timber.timber import Timber
    from CynanBotCommon.trivia.absTriviaQuestion import AbsTriviaQuestion
    from CynanBotCommon.trivia.multipleChoiceTriviaQuestion import \
        MultipleChoiceTriviaQuestion
    from CynanBotCommon.trivia.questionAnswerTriviaQuestion import \
        QuestionAnswerTriviaQuestion
    from CynanBotCommon.trivia.triviaAnswerCheckResult import \
        TriviaAnswerCheckResult
    from CynanBotCommon.trivia.triviaAnswerCompiler import TriviaAnswerCompiler
    from CynanBotCommon.trivia.triviaExceptions import (
        BadTriviaAnswerException, UnsupportedTriviaTypeException)
    from CynanBotCommon.trivia.triviaSettingsRepository import \
        TriviaSettingsRepository
    from CynanBotCommon.trivia.triviaType import TriviaType
    from CynanBotCommon.trivia.trueFalseTriviaQuestion import \
        TrueFalseTriviaQuestion
except:
    import utils
    from timber.timber import Timber

    from trivia.absTriviaQuestion import AbsTriviaQuestion
    from trivia.multipleChoiceTriviaQuestion import \
        MultipleChoiceTriviaQuestion
    from trivia.questionAnswerTriviaQuestion import \
        QuestionAnswerTriviaQuestion
    from trivia.triviaAnswerCheckResult import TriviaAnswerCheckResult
    from trivia.triviaAnswerCompiler import TriviaAnswerCompiler
    from trivia.triviaExceptions import (BadTriviaAnswerException,
                                         UnsupportedTriviaTypeException)
    from trivia.triviaSettingsRepository import TriviaSettingsRepository
    from trivia.triviaType import TriviaType
    from trivia.trueFalseTriviaQuestion import TrueFalseTriviaQuestion


class TriviaAnswerChecker():

    def __init__(
        self,
        timber: Timber,
        triviaAnswerCompiler: TriviaAnswerCompiler,
        triviaSettingsRepository: TriviaSettingsRepository,
    ):
        if timber is None:
            raise ValueError(f'timber argument is malformed: \"{timber}\"')
        elif triviaAnswerCompiler is None:
            raise ValueError(f'triviaAnswerCompiler argument is malformed: \"{triviaAnswerCompiler}\"')
        elif triviaSettingsRepository is None:
            raise ValueError(f'triviaSettingsRepository argument is malformed: \"{triviaSettingsRepository}\"')

        self.__timber: Timber = timber
        self.__triviaAnswerCompiler: TriviaAnswerCompiler = triviaAnswerCompiler
        self.__triviaSettingsRepository: TriviaSettingsRepository = triviaSettingsRepository

        self.__digitPattern: Pattern = re.compile(r'(\d+)')
        self.__whitespacePattern: Pattern = re.compile(r'\s\s+')

        self.__irregular_nouns: Dict[str, str] = {
            'child': 'children',
            'goose': 'geese',
            'man': 'men',
            'woman': 'women',
            'person': 'people',
            'tooth': 'teeth',
            'foot': 'feet',
            'mouse': 'mice',
            'die': 'dice',
            'ox': 'oxen',
            'index': 'indices',
        }

        self.__stopwords: List[str] = (
            'i', 'me', 'my', 'myself', 'we', 'ourselves', 'you', 'he', 'him', 'his', 'she', 'they', 'them',  'what',
            'which', 'who', 'whom', 'this', 'that', 'these', 'those', 'am', 'is', 'are', 'was', 'were', 'be', 'been',
            'being', 'have', 'has', 'had', 'having', 'do', 'does', 'did', 'doing', 'a', 'an', 'the', 'and', 'but', 'if',
            'or', 'because', 'as', 'until', 'while', 'of', 'at', 'by', 'for', 'with', 'about', 'against', 'between',
            'into', 'through', 'during', 'before', 'after', 'above', 'below', 'to', 'from', 'up', 'down', 'in', 'out',
            'on', 'off', 'over', 'under', 'again', 'further', 'then', 'once', 'here', 'there', 'when', 'where', 'why',
            'how', 'all', 'any', 'both', 'each', 'few', 'more', 'most', 'some', 'such', 'nor', 'not', 'only',
            'own', 'same', 'so', 'than', 'too', 'very', 'can', 'will', 'just', 'dont', 'should', 'now',
        )

    async def checkAnswer(
        self,
        answer: Optional[str],
        triviaQuestion: AbsTriviaQuestion,
        extras: Optional[Dict[str, Any]] = None
    ) -> TriviaAnswerCheckResult:
        if triviaQuestion is None:
            raise ValueError(f'triviaQuestion argument is malformed: \"{triviaQuestion}\"')

        if not utils.isValidStr(answer):
            return TriviaAnswerCheckResult.INVALID_INPUT

        if triviaQuestion.getTriviaType() is TriviaType.MULTIPLE_CHOICE:
            return await self.__checkAnswerMultipleChoice(answer, triviaQuestion)
        elif triviaQuestion.getTriviaType() is TriviaType.QUESTION_ANSWER:
            return await self.__checkAnswerQuestionAnswer(answer, triviaQuestion, extras)
        elif triviaQuestion.getTriviaType() is TriviaType.TRUE_FALSE:
            return await self.__checkAnswerTrueFalse(answer, triviaQuestion)
        else:
            raise UnsupportedTriviaTypeException(f'Unsupported TriviaType: \"{triviaQuestion.getTriviaType()}\"')

    async def __checkAnswerMultipleChoice(
        self,
        answer: Optional[str],
        triviaQuestion: MultipleChoiceTriviaQuestion
    ) -> TriviaAnswerCheckResult:
        if triviaQuestion is None:
            raise ValueError(f'triviaQuestion argument is malformed: \"{triviaQuestion}\"')
        elif triviaQuestion.getTriviaType() is not TriviaType.MULTIPLE_CHOICE:
            raise RuntimeError(f'TriviaType is not {TriviaType.MULTIPLE_CHOICE}: \"{triviaQuestion.getTriviaType()}\"')

        answerOrdinal: int = None
        try:
            answerOrdinal = await self.__triviaAnswerCompiler.compileTextAnswerToMultipleChoiceOrdinal(answer)
        except BadTriviaAnswerException as e:
            self.__timber.log('TriviaAnswerChecker', f'Unable to convert multiple choice answer to ordinal: \"{answer}\": {e}')
            return TriviaAnswerCheckResult.INVALID_INPUT

        if not utils.isValidNum(answerOrdinal):
            # this should be impossible, but let's just check anyway
            self.__timber.log('TriviaAnswerChecker', f'Unable to convert multiple choice answer to ordinal: (answer=\"{answer}\", answerOrdinal={answerOrdinal})')
            return TriviaAnswerCheckResult.INVALID_INPUT

        answerOrdinals = triviaQuestion.getAnswerOrdinals()

        if answerOrdinal < 0 or answerOrdinal >= len(answerOrdinals):
            # Checks for a scenario where the user guessed an answer outside the range
            # of actual responses. For example, the user might have guessed F, but the
            # question only had up to D.
            self.__timber.log('TriviaAnswerChecker', f'Multiple choice answer ordinal ({answerOrdinal}) is outside the range of actual answer ordinals: {answerOrdinals}')
            return TriviaAnswerCheckResult.INVALID_INPUT

        if answerOrdinal in triviaQuestion.getCorrectAnswerOrdinals():
            return TriviaAnswerCheckResult.CORRECT
        else:
            return TriviaAnswerCheckResult.INCORRECT

    async def __checkAnswerQuestionAnswer(
        self,
        answer: Optional[str],
        triviaQuestion: QuestionAnswerTriviaQuestion,
        extras: Optional[Dict[str, Any]] = None
    ) -> TriviaAnswerCheckResult:
        if triviaQuestion is None:
            raise ValueError(f'triviaQuestion argument is malformed: \"{triviaQuestion}\"')
        elif triviaQuestion.getTriviaType() is not TriviaType.QUESTION_ANSWER:
            raise RuntimeError(f'TriviaType is not {TriviaType.QUESTION_ANSWER}: \"{triviaQuestion.getTriviaType()}\"')

        cleanedAnswers = await self.__triviaAnswerCompiler.compileTextAnswersList([answer], False)

        if not all(utils.isValidStr(cleanedAnswer) for cleanedAnswer in cleanedAnswers):
            return TriviaAnswerCheckResult.INCORRECT

        correctAnswers = triviaQuestion.getCorrectAnswers()
        cleanedCorrectAnswers = triviaQuestion.getCleanedCorrectAnswers()

        self.__timber.log('TriviaAnswerChecker', f'answer:\"{answer}\", cleanedAnswers:\"{cleanedAnswers}\", correctAnswers:\"{correctAnswers}\", cleanedCorrectAnswers:\"{cleanedCorrectAnswers}\", extras:\"{extras}\"')

        for cleanedCorrectAnswer in cleanedCorrectAnswers:
            for cleanedAnswer in cleanedAnswers:
                for guess in await self.__triviaAnswerCompiler.expandNumerals(cleanedAnswer):
                    if guess == cleanedCorrectAnswer:
                        return TriviaAnswerCheckResult.CORRECT
                    guessWords = self.__whitespacePattern.sub(' ', guess).split(' ')
                    answerWords = self.__whitespacePattern.sub(' ', cleanedCorrectAnswer).split(' ')

                    minWords = min(len(guessWords), len(answerWords))

                    for gWords in self.__mergeWords(guessWords, minWords):
                        for aWords in self.__mergeWords(answerWords, minWords):
                            # This expansion of all() is required because you can't perform list comprehension on async
                            #   generators yet. :(
                            valid = True
                            for i in range(len(gWords)):
                                if not await self.__compareWords(gWords[i], aWords[i]):
                                    valid = False
                                    break
                            if valid:
                                return TriviaAnswerCheckResult.CORRECT

        return TriviaAnswerCheckResult.INCORRECT

    async def __checkAnswerTrueFalse(
        self,
        answer: Optional[str],
        triviaQuestion: TrueFalseTriviaQuestion
    ) -> TriviaAnswerCheckResult:
        if triviaQuestion is None:
            raise ValueError(f'triviaQuestion argument is malformed: \"{triviaQuestion}\"')
        elif triviaQuestion.getTriviaType() is not TriviaType.TRUE_FALSE:
            raise RuntimeError(f'TriviaType is not {TriviaType.TRUE_FALSE}: \"{triviaQuestion.getTriviaType()}\"')

        answerBool: bool = None
        try:
            answerBool = await self.__triviaAnswerCompiler.compileBoolAnswer(answer)
        except BadTriviaAnswerException as e:
            self.__timber.log('TriviaAnswerChecker', f'Unable to convert true false answer to bool: \"{answer}\": {e}')
            return TriviaAnswerCheckResult.INVALID_INPUT

        if answerBool in triviaQuestion.getCorrectAnswerBools():
            return TriviaAnswerCheckResult.CORRECT
        else:
            return TriviaAnswerCheckResult.INCORRECT

    # generates all possible groupings of the given words such that the resulting word count is target_length
    # example: words = ["a", "b", "c", "d"], target_length = 2
    #          generates ["abc", "d"], ["ab", "cd"], ["a", "bcd"]
    def __mergeWords(self, wordList: List[str], target_length: int) -> Generator[List[str], None, None]:
        if len(wordList) <= target_length:
            yield wordList
        else:
            for i in range(len(wordList) - 1):
                # merge the ith and i+1th word
                w = wordList[:]
                p = w.pop(i+1)
                w[i] += p
                # recurse on the new merged set until target length is reached
                yield from self.__mergeWords(w, target_length)

    # compare two individual words, returns true if any valid variants match between the two words
    async def __compareWords(self, word1: str, word2: str) -> bool:
        thresholdGrowthRate = await self.__triviaSettingsRepository.getLevenshteinThresholdGrowthRate()
        for w1 in self.__genVariantPossibilities(word1):
            for w2 in self.__genVariantPossibilities(word2):
                # calculate threshold based on shorter word length
                threshold = math.floor(min(len(w1), len(w2)) / thresholdGrowthRate)
                dist = polyleven.levenshtein(w1, w2, threshold + 1)
                if dist <= threshold:
                    return True
        return False

    def __genVariantPossibilities(self, word: str) -> Generator[str, None, None]:
        # don't preprocess stopwords
        if word in self.__stopwords:
            yield word
        else:
            yield word
            # pluralizations
            if any(word.endswith(s) for s in ('ss', 'sh', 'ch', 'x', 'z', 's', 'o')):
                yield word+'es'
            if word[-1] in 'sz':
                yield word + word[-1] + 'es'
            elif word.endswith('f'):
                yield word[:-1] + 'ves'
            elif word.endswith('fe'):
                yield word[:-2] + 'ves'
            elif word[-1] == 'y' and len(word) > 1 and word[-2] not in 'aeiou':
                yield word[:-1] + 'ies'
            elif word.endswith('us'):
                yield word[:-2] + 'i'
            elif word.endswith('is'):
                yield word[:-2] + 'es'
            elif word.endswith('on') or word.endswith('um'):
                yield word[:-2] + 'a'
            if word in self.__irregular_nouns:
                yield self.__irregular_nouns[word]
            if word[-1] != 's':
                yield word + 's'

            # titles
            if word == 'jr':
                yield 'junior'
            if word == 'sr':
                yield 'senior'
            if word == 'mr':
                yield 'mister'
            if word == 'ms':
                yield 'miss'
            if word == 'mrs':
                yield 'missus'

            # streets
            if word == 'ave':
                yield 'avenue'
            if word == 'blvd':
                yield 'boulevard'
            if word in ('ct', 'crt'):
                yield 'court'
            if word == 'dr':
                yield 'drive'
                yield 'doctor'
            if word == 'st':
                yield 'street'
                yield 'saint'
            if word == 'rd':
                yield 'road'
            if word == 'pl':
                yield 'place'
            if word == 'sq':
                yield 'square'
            if word == 'stn':
                yield 'station'

            # directions
            if word == 'n':
                yield 'north'
            if word == 's':
                yield 'south'
            if word == 'e':
                yield 'east'
            if word == 'w':
                yield 'west'
            if word == 'nw':
                yield 'northwest'
            if word == 'ne':
                yield 'northeast'
            if word == 'sw':
                yield 'southwest'
            if word == 'se':
                yield 'southeast'

            # other
            if word == 'dept':
                yield 'department'
            if word == 'no':
                yield 'number'
            if word == 'vs':
                yield 'versus'
            if word == 'mt':
                yield 'mount'

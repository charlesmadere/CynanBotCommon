import math
import re
import polyleven

try:
    import CynanBotCommon.utils as utils
    from CynanBotCommon.timber.timber import Timber
    from CynanBotCommon.trivia.absTriviaQuestion import AbsTriviaQuestion
    from CynanBotCommon.trivia.multipleChoiceTriviaQuestion import \
        MultipleChoiceTriviaQuestion
    from CynanBotCommon.trivia.questionAnswerTriviaQuestion import \
        QuestionAnswerTriviaQuestion
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

        self.__digitPattern = re.compile(r'(\d+)')
        self.__whitespacePattern = re.compile(r'\s\s+')

        self.__irregular_nouns = {
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

        self.__stopwords = (
            'i', 'me', 'my', 'myself', 'we', 'ourselves', 'you', 'he', 'him', 'his', 'she', 'they', 'them',  'what',
            'which', 'who', 'whom', 'this', 'that', 'these', 'those', 'am', 'is', 'are', 'was', 'were', 'be', 'been',
            'being', 'have', 'has', 'had', 'having', 'do', 'does', 'did', 'doing', 'a', 'an', 'the', 'and', 'but', 'if',
            'or', 'because', 'as', 'until', 'while', 'of', 'at', 'by', 'for', 'with', 'about', 'against', 'between',
            'into', 'through', 'during', 'before', 'after', 'above', 'below', 'to', 'from', 'up', 'down', 'in', 'out',
            'on', 'off', 'over', 'under', 'again', 'further', 'then', 'once', 'here', 'there', 'when', 'where', 'why',
            'how', 'all', 'any', 'both', 'each', 'few', 'more', 'most', 'some', 'such', 'nor', 'not', 'only',
            'own', 'same', 'so', 'than', 'too', 'very', 'can', 'will', 'just', 'dont', 'should', 'now',
        )

    async def checkAnswer(self, answer: str, triviaQuestion: AbsTriviaQuestion) -> bool:
        if triviaQuestion is None:
            raise ValueError(f'triviaQuestion argument is malformed: \"{triviaQuestion}\"')

        if not utils.isValidStr(answer):
            return False

        if triviaQuestion.getTriviaType() is TriviaType.MULTIPLE_CHOICE:
            return await self.__checkAnswerMultipleChoice(answer, triviaQuestion)
        elif triviaQuestion.getTriviaType() is TriviaType.QUESTION_ANSWER:
            return await self.__checkAnswerQuestionAnswer(answer, triviaQuestion)
        elif triviaQuestion.getTriviaType() is TriviaType.TRUE_FALSE:
            return await self.__checkAnswerTrueFalse(answer, triviaQuestion)
        else:
            raise UnsupportedTriviaTypeException(f'Unsupported TriviaType: \"{triviaQuestion.getTriviaType()}\"')

    async def __checkAnswerMultipleChoice(
        self,
        answer: str,
        triviaQuestion: MultipleChoiceTriviaQuestion
    ) -> bool:
        if triviaQuestion is None:
            raise ValueError(f'triviaQuestion argument is malformed: \"{triviaQuestion}\"')
        elif triviaQuestion.getTriviaType() is not TriviaType.MULTIPLE_CHOICE:
            raise RuntimeError(f'TriviaType is not {TriviaType.MULTIPLE_CHOICE}: \"{triviaQuestion.getTriviaType()}\"')

        answerOrdinal: int = None
        try:
            answerOrdinal = await self.__triviaAnswerCompiler.compileTextAnswerToMultipleChoiceOrdinal(answer)
        except BadTriviaAnswerException as e:
            self.__timber.log('TriviaAnswerChecker', f'Unable to convert multiple choice answer to ordinal: \"{answer}\": {e}')
            return False

        return answerOrdinal in triviaQuestion.getCorrectAnswerOrdinals()

    async def __checkAnswerQuestionAnswer(
        self,
        answer: str,
        triviaQuestion: QuestionAnswerTriviaQuestion
    ) -> bool:
        if triviaQuestion is None:
            raise ValueError(f'triviaQuestion argument is malformed: \"{triviaQuestion}\"')
        elif triviaQuestion.getTriviaType() is not TriviaType.QUESTION_ANSWER:
            raise RuntimeError(f'TriviaType is not {TriviaType.QUESTION_ANSWER}: \"{triviaQuestion.getTriviaType()}\"')

        cleanedAnswers = await self.__triviaAnswerCompiler.compileTextAnswersList([answer], False)
        print(f'cleaned={cleanedAnswers}')
        if not all(utils.isValidStr(cleanedAnswer) for cleanedAnswer in cleanedAnswers):
            return False

        correctAnswers = triviaQuestion.getCorrectAnswers()
        cleanedCorrectAnswers = triviaQuestion.getCleanedCorrectAnswers()

        # levenshteinAnswerLengthsActivationThreshold = await self.__triviaSettingsRepository.getLevenshteinAnswerLengthsActivationThreshold()
        # levenshteinAnswerLengthsRoundUpThreshold = await self.__triviaSettingsRepository.getLevenshteinAnswerLengthsRoundUpThreshold()
        # maxLevenshteinDistance = await self.__triviaSettingsRepository.getMaxLevenshteinDistance()
        # isAdditionalPluralCheckingEnabled = await self.__triviaSettingsRepository.isAdditionalPluralCheckingEnabled()
        # isDebugLoggingEnabled = await self.__triviaSettingsRepository.isDebugLoggingEnabled()

        for cleanedCorrectAnswer in cleanedCorrectAnswers:
            for cleanedAnswer in cleanedAnswers:
                for guess in await self.__triviaAnswerCompiler.expandNumerals(cleanedAnswer):
                    print(guess)
                    if guess == cleanedCorrectAnswer:
                        return True
                    guessWords = self.__whitespacePattern.sub(' ', guess).split(' ')
                    answerWords = self.__whitespacePattern.sub(' ', cleanedCorrectAnswer).split(' ')

                    minWords = min(len(guessWords), len(answerWords))

                    for gWords in self.__mergeWords(guessWords, minWords):
                        for aWords in self.__mergeWords(answerWords, minWords):
                            if all(self.__compareWords(gWords[i], aWords[i]) for i in range(len(gWords))):
                                return True

        return False

    async def __checkAnswerTrueFalse(
        self,
        answer: str,
        triviaQuestion: TrueFalseTriviaQuestion
    ) -> bool:
        if triviaQuestion is None:
            raise ValueError(f'triviaQuestion argument is malformed: \"{triviaQuestion}\"')
        elif triviaQuestion.getTriviaType() is not TriviaType.TRUE_FALSE:
            raise RuntimeError(f'TriviaType is not {TriviaType.TRUE_FALSE}: \"{triviaQuestion.getTriviaType()}\"')

        answerBool: bool = None
        try:
            answerBool = await self.__triviaAnswerCompiler.compileBoolAnswer(answer)
        except BadTriviaAnswerException as e:
            self.__timber.log('TriviaAnswerChecker', f'Unable to convert true false answer to bool: \"{answer}\": {e}')
            return False

        return answerBool in triviaQuestion.getCorrectAnswerBools()

    # generates all possible groupings of the given words such that the resulting word count is target_length
    # example: words = ["a", "b", "c", "d"], target_length = 2
    #          returns ["abc", "d"], ["ab", "cd"], ["a", "bcd"]
    def __mergeWords(self, wordList, target_length):
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

    # compare two individual words, returns minimal edit distance of all valid versions of each word
    def __compareWords(self, word1, word2):
        for w1 in self.__genVariantPossibilities(word1):
            for w2 in self.__genVariantPossibilities(word2):
                threshold = math.floor(min(len(w1), len(w2)) / 7)  # calculate threshold based on min(len(w1), len(w2))
                dist = polyleven.levenshtein(w1, w2, threshold + 1)
                if dist <= threshold:
                    return True
        return False

    def __genVariantPossibilities(self, word):
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
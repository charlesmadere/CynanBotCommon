import math
import re
import polyleven
from num2words import num2words
import roman


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

        self.__maxEditDistance = 10000  # Larger than any Twitch chat message can be

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

        cleanedAnswer = await self.__triviaAnswerCompiler.compileTextAnswer(answer)

        if not utils.isValidStr(cleanedAnswer):
            return False

        correctAnswers = triviaQuestion.getCorrectAnswers()
        cleanedCorrectAnswers = triviaQuestion.getCleanedCorrectAnswers()

        levenshteinAnswerLengthsActivationThreshold = await self.__triviaSettingsRepository.getLevenshteinAnswerLengthsActivationThreshold()
        levenshteinAnswerLengthsRoundUpThreshold = await self.__triviaSettingsRepository.getLevenshteinAnswerLengthsRoundUpThreshold()
        maxLevenshteinDistance = await self.__triviaSettingsRepository.getMaxLevenshteinDistance()
        isAdditionalPluralCheckingEnabled = await self.__triviaSettingsRepository.isAdditionalPluralCheckingEnabled()
        isDebugLoggingEnabled = await self.__triviaSettingsRepository.isDebugLoggingEnabled()

        for cleanedCorrectAnswer in cleanedCorrectAnswers:
            if cleanedAnswer == cleanedCorrectAnswer:
                return True
            guessWords = self.__whitespacePattern.sub(' ', cleanedAnswer).split(' ')
            answerWords = self.__whitespacePattern.sub(' ', cleanedCorrectAnswer).split(' ')

            minWords = min(len(guessWords), len(answerWords))

            for gWords in self.__mergeWords(guessWords, minWords):
                for aWords in self.__mergeWords(answerWords, minWords):
                    if all(self.__compareWords(gWords[i], aWords[i]) for i in range(len(gWords))):
                        return True
            return False

        # for cleanedCorrectAnswer in cleanedCorrectAnswers:
        #     if cleanedAnswer == cleanedCorrectAnswer:
        #         return True

        #     cleanedAnswerLen: int = len(cleanedAnswer)
        #     cleanedCorrectAnswerLen: int = len(cleanedCorrectAnswer)
        #     rawThreshold: float = min(cleanedAnswerLen, cleanedCorrectAnswerLen) * levenshteinAnswerLengthsActivationThreshold
        #     rawThresholdDecimal: float = rawThreshold % 1.0

        #     threshold: int = 0
        #     if rawThresholdDecimal > levenshteinAnswerLengthsRoundUpThreshold:
        #         threshold = int(math.ceil(rawThreshold))
        #     elif rawThresholdDecimal < levenshteinAnswerLengthsRoundUpThreshold:
        #         threshold = int(math.floor(rawThreshold))
        #     else:
        #         threshold = int(round(rawThreshold))

        #     threshold = int(min(threshold, maxLevenshteinDistance))
        #     distance: int = self.__digitlessDistanceCheck(cleanedAnswer, cleanedCorrectAnswer, threshold)

        #     if isDebugLoggingEnabled:
        #         self.__timber.log('TriviaAnswerChecker', f'answer:\"{answer}\", cleanedAnswer:\"{cleanedAnswer}\", correctAnswers:\"{correctAnswers}\", cleanedCorrectAnswers:\"{cleanedCorrectAnswers}\", threshold:\"{threshold}\", distance:\"{distance}\", levenshteinAnswerLengthsActivationThreshold:\"{levenshteinAnswerLengthsActivationThreshold}\", maxLevenshteinDistance:\"{maxLevenshteinDistance}\"')

        #     if distance <= threshold:
        #         return True

            # if isAdditionalPluralCheckingEnabled:
            #     if cleanedCorrectAnswer.endswith('s'):
            #         continue
            #     elif cleanedCorrectAnswer.endswith('y'):
            #         cleanedCorrectAnswer = f'{cleanedCorrectAnswer[0:len(cleanedCorrectAnswer) - 1]}ies'
            #     else:
            #         cleanedCorrectAnswer = f'{cleanedCorrectAnswer}s'

            #     if cleanedAnswer == cleanedCorrectAnswer:
            #         return True

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

    def __digitlessDistanceCheck(self, guess, correctAnswer, threshold=-1):
        guessParts = self.__digitPattern.split(guess)
        answerParts = self.__digitPattern.split(correctAnswer)
        guessWords = guessParts[::2]
        guessNumbers = guessParts[1::2]
        answerWords = answerParts[::2]
        answerNumbers = answerParts[1::2]
        if (guessNumbers != answerNumbers):
            return 500  # Max message length, impossible to be correct answer.
        return polyleven.levenshtein(''.join(guessWords), ''.join(answerWords), threshold)

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
        m = self.__maxEditDistance
        for w1 in self.__triviaAnswerCompiler.__genPluralPossibilities(word1):
            for w2 in self.__triviaAnswerCompiler.__genPluralPossibilities(word2):
                threshold = math.floor(min(len(w1), len(w2)) / 6)  # calculate threshold based on`min(len(w1), len(w2))
                dist = polyleven.levenshtein(w1, w2, threshold + 1)
                if dist <= threshold:
                    return m
        return m
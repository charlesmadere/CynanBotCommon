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
        maxLevenshteinDistance = await self.__triviaSettingsRepository.getMaxLevenshteinDistance()
        isAdditionalPluralCheckingEnabled = await self.__triviaSettingsRepository.isAdditionalPluralCheckingEnabled()
        isDebugLoggingEnabled = await self.__triviaSettingsRepository.isDebugLoggingEnabled()

        for cleanedCorrectAnswer in cleanedCorrectAnswers:
            if cleanedAnswer == cleanedCorrectAnswer:
                return True

            # Check the answer for any digits. We do this to prevent there being any flexibility
            # on answers that are number-based. This prevents issues that could occur where the
            # correct answer is "19th century" but the user guessed "18th century."
            if utils.containsDigit(cleanedCorrectAnswer):
                continue

            cleanedAnswerLen: int = len(cleanedAnswer)
            cleanedCorrectAnswerLen: int = len(cleanedCorrectAnswer)

            threshold: int = int(min(cleanedAnswerLen, cleanedCorrectAnswerLen) * levenshteinAnswerLengthsActivationThreshold)
            actualDistance: int = polyleven.levenshtein(cleanedAnswer, cleanedCorrectAnswer, threshold)

            if isDebugLoggingEnabled:
                self.__timber.log('TriviaAnswerChecker', f'answer:\"{answer}\", cleanedAnswer:\"{cleanedAnswer}\", correctAnswers:\"{correctAnswers}\", cleanedCorrectAnswers:\"{cleanedCorrectAnswers}\", threshold:\"{threshold}\", actualDistance:\"{actualDistance}\", levenshteinAnswerLengthsActivationThreshold:\"{levenshteinAnswerLengthsActivationThreshold}\", maxLevenshteinDistance:\"{maxLevenshteinDistance}\"')

            if actualDistance <= threshold:
                return True

            if isAdditionalPluralCheckingEnabled:
                if cleanedCorrectAnswer.endswith('s'):
                    continue
                elif cleanedCorrectAnswer.endswith('y'):
                    cleanedCorrectAnswer = f'{cleanedCorrectAnswer[0:len(cleanedCorrectAnswer) - 1]}ies'
                else:
                    cleanedCorrectAnswer = f'{cleanedCorrectAnswer}s'

                if cleanedAnswer == cleanedCorrectAnswer:
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

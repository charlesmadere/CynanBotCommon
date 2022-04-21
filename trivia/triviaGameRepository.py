import asyncio
import re
from asyncio import AbstractEventLoop
from datetime import datetime, timezone
from queue import SimpleQueue
from typing import Dict, List, Pattern

try:
    import CynanBotCommon.utils as utils
    from CynanBotCommon.timber.timber import Timber
    from CynanBotCommon.trivia.absTriviaAction import AbsTriviaAction
    from CynanBotCommon.trivia.absTriviaEvent import AbsTriviaEvent
    from CynanBotCommon.trivia.absTriviaQuestion import AbsTriviaQuestion
    from CynanBotCommon.trivia.checkAnswerTriviaAction import \
        CheckAnswerTriviaAction
    from CynanBotCommon.trivia.correctAnswerTriviaEvent import \
        CorrectAnswerTriviaEvent
    from CynanBotCommon.trivia.failedToFetchQuestionTriviaEvent import \
        FailedToFetchQuestionTriviaEvent
    from CynanBotCommon.trivia.gameAlreadyInProgressTriviaEvent import \
        GameAlreadyInProgressTriviaEvent
    from CynanBotCommon.trivia.gameNotReadyCheckAnswerTriviaEvent import \
        GameNotReadyCheckAnswerTriviaEvent
    from CynanBotCommon.trivia.incorrectAnswerTriviaEvent import \
        IncorrectAnswerTriviaEvent
    from CynanBotCommon.trivia.multipleChoiceTriviaQuestion import \
        MultipleChoiceTriviaQuestion
    from CynanBotCommon.trivia.newGameTriviaEvent import NewGameTriviaEvent
    from CynanBotCommon.trivia.outOfTimeCheckAnswerTriviaEvent import \
        OutOfTimeCheckAnswerTriviaEvent
    from CynanBotCommon.trivia.outOfTimeTriviaEvent import OutOfTimeTriviaEvent
    from CynanBotCommon.trivia.questionAnswerTriviaQuestion import \
        QuestionAnswerTriviaQuestion
    from CynanBotCommon.trivia.startNewGameTriviaAction import \
        StartNewGameTriviaAction
    from CynanBotCommon.trivia.triviaActionType import TriviaActionType
    from CynanBotCommon.trivia.triviaExceptions import (
        TooManyTriviaFetchAttemptsException, UnknownTriviaActionTypeException)
    from CynanBotCommon.trivia.triviaGameState import TriviaGameState
    from CynanBotCommon.trivia.triviaRepository import TriviaRepository
    from CynanBotCommon.trivia.triviaScoreRepository import \
        TriviaScoreRepository
    from CynanBotCommon.trivia.triviaType import TriviaType
    from CynanBotCommon.trivia.trueFalseTriviaQuestion import \
        TrueFalseTriviaQuestion
    from CynanBotCommon.trivia.wrongUserCheckAnswerTriviaEvent import \
        WrongUserCheckAnswerTriviaEvent
except:
    import utils
    from timber.timber import Timber

    from trivia.absTriviaAction import AbsTriviaAction
    from trivia.absTriviaEvent import AbsTriviaEvent
    from trivia.absTriviaQuestion import AbsTriviaQuestion
    from trivia.checkAnswerTriviaAction import CheckAnswerTriviaAction
    from trivia.correctAnswerTriviaEvent import CorrectAnswerTriviaEvent
    from trivia.failedToFetchQuestionTriviaEvent import \
        FailedToFetchQuestionTriviaEvent
    from trivia.gameAlreadyInProgressTriviaEvent import \
        GameAlreadyInProgressTriviaEvent
    from trivia.gameNotReadyCheckAnswerTriviaEvent import \
        GameNotReadyCheckAnswerTriviaEvent
    from trivia.incorrectAnswerTriviaEvent import IncorrectAnswerTriviaEvent
    from trivia.multipleChoiceTriviaQuestion import \
        MultipleChoiceTriviaQuestion
    from trivia.newGameTriviaEvent import NewGameTriviaEvent
    from trivia.outOfTimeCheckAnswerTriviaEvent import \
        OutOfTimeCheckAnswerTriviaEvent
    from trivia.outOfTimeTriviaEvent import OutOfTimeTriviaEvent
    from trivia.questionAnswerTriviaQuestion import \
        QuestionAnswerTriviaQuestion
    from trivia.startNewGameTriviaAction import StartNewGameTriviaAction
    from trivia.triviaActionType import TriviaActionType
    from trivia.triviaExceptions import (TooManyTriviaFetchAttemptsException,
                                         UnknownTriviaActionTypeException)
    from trivia.triviaGameState import TriviaGameState
    from trivia.triviaRepository import TriviaRepository
    from trivia.triviaScoreRepository import TriviaScoreRepository
    from trivia.triviaType import TriviaType
    from trivia.trueFalseTriviaQuestion import TrueFalseTriviaQuestion
    from trivia.wrongUserCheckAnswerTriviaEvent import \
        WrongUserCheckAnswerTriviaEvent


class TriviaGameRepository():

    def __init__(
        self,
        eventLoop: AbstractEventLoop,
        timber: Timber,
        triviaRepository: TriviaRepository,
        triviaScoreRepository: TriviaScoreRepository,
        sleepTimeSeconds: float = 0.5
    ):
        if eventLoop is None:
            raise ValueError(f'eventLoop argument is malformed: \"{eventLoop}\"')
        elif timber is None:
            raise ValueError(f'timber argument is malformed: \"{timber}\"')
        elif triviaRepository is None:
            raise ValueError(f'triviaRepository argument is malformed: \"{triviaRepository}\"')
        elif triviaScoreRepository is None:
            raise ValueError(f'triviaScoreRepository argument is malformed: \"{triviaScoreRepository}\"')
        elif not utils.isValidNum(sleepTimeSeconds):
            raise ValueError(f'sleepTimeSeconds argument is malformed: \"{sleepTimeSeconds}\"')
        elif sleepTimeSeconds < 0.1 or sleepTimeSeconds > 5:
            raise ValueError(f'sleepTimeSeconds argument is out of bounds: {sleepTimeSeconds}')

        self.__timber: Timber = timber
        self.__triviaRepository: TriviaRepository = triviaRepository
        self.__triviaScoreRepository: TriviaScoreRepository = triviaScoreRepository
        self.__sleepTimeSeconds: float = sleepTimeSeconds

        self.__states: Dict[str, TriviaGameState] = dict()
        self.__fullWordAnswerRegEx: Pattern = re.compile(r"\w+|\d+", re.IGNORECASE)
        self.__multipleChoiceAnswerRegEx: Pattern = re.compile(r"[a-z]", re.IGNORECASE)
        self.__eventListener = None

        self.__actionQueue: SimpleQueue[AbsTriviaAction] = SimpleQueue()
        self.__eventQueue: SimpleQueue[AbsTriviaEvent] = SimpleQueue()
        eventLoop.create_task(self.__startActionLoop())
        eventLoop.create_task(self.__startEventLoop())

    async def __applyAnswerCleanup(self, text: str) -> str:
        if not utils.isValidStr(text):
            return ''

        text = text.lower()
        regexResult = self.__fullWordAnswerRegEx.findall(text)
        return ''.join(regexResult)

    async def __checkAnswer(self, answer: str, triviaQuestion: AbsTriviaQuestion) -> bool:
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
            raise RuntimeError(f'Unsupported TriviaType: \"{triviaQuestion.getTriviaType()}\"')

    async def __checkAnswerMultipleChoice(self, answer: str, triviaQuestion: MultipleChoiceTriviaQuestion) -> bool:
        if triviaQuestion is None:
            raise ValueError(f'triviaQuestion argument is malformed: \"{triviaQuestion}\"')
        elif triviaQuestion.getTriviaType() is not TriviaType.MULTIPLE_CHOICE:
            raise RuntimeError(f'TriviaType is not {TriviaType.MULTIPLE_CHOICE}: \"{triviaQuestion.getTriviaType()}\"')

        answer = await self.__applyAnswerCleanup(answer)

        if not utils.isValidStr(answer) or len(answer) != 1:
            return False
        elif self.__multipleChoiceAnswerRegEx.fullmatch(answer) is None:
            return False

        # this converts the answer 'A' into 0, 'B' into 1, 'C' into 2, and so on...
        index = ord(answer.upper()) % 65

        return index in triviaQuestion.getCorrectAnswerOrdinals()

    async def __checkAnswerQuestionAnswer(self, answer: str, triviaQuestion: QuestionAnswerTriviaQuestion) -> bool:
        if triviaQuestion is None:
            raise ValueError(f'triviaQuestion argument is malformed: \"{triviaQuestion}\"')
        elif triviaQuestion.getTriviaType() is not TriviaType.QUESTION_ANSWER:
            raise RuntimeError(f'TriviaType is not {TriviaType.QUESTION_ANSWER}: \"{triviaQuestion.getTriviaType()}\"')

        cleanedAnswer = await self.__applyAnswerCleanup(answer)
        correctAnswers = triviaQuestion.getCorrectAnswers()

        for correctAnswer in correctAnswers:
            cleanedCorrectAnswer = await self.__applyAnswerCleanup(correctAnswer)

            # This if statement prevents a potentially really weird edge case of the correctanswer
            # being something that is dropped completely from the string in the applyAnswerCleanup()
            # method. So here, we have to fall back to just checking the raw answer strings, as we
            # have nothing else to go on.
            if utils.isValidStr(cleanedCorrectAnswer) and cleanedAnswer == cleanedCorrectAnswer:
                return True
            elif answer.lower() == correctAnswer.lower():
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

        answer = await self.__applyAnswerCleanup(answer)

        if not utils.isValidStr(answer):
            return False

        answerBool = utils.strToBool(answer)
        return answerBool in triviaQuestion.getCorrectAnswerBools()

    async def __handleActionCheckAnswer(self, action: CheckAnswerTriviaAction):
        if action is None:
            raise ValueError(f'action argument is malformed: \"{action}\"')
        elif action.getTriviaActionType() is not TriviaActionType.CHECK_ANSWER:
            raise RuntimeError(f'TriviaActionType is not {TriviaActionType.CHECK_ANSWER}: \"{action.getTriviaActionType()}\"')

        state = self.__states.get(action.getTwitchChannel().lower())
        if state is None:
            await self.__eventQueue.put(GameNotReadyCheckAnswerTriviaEvent(
                answer = action.getAnswer(),
                twitchChannel = action.getTwitchChannel(),
                userId = action.getUserId(),
                userName = action.getUserName()
            ))
            return

        if state.getUserId() != action.getUserId():
            await self.__eventQueue.put(WrongUserCheckAnswerTriviaEvent(
                answer = action.getAnswer(),
                twitchChannel = action.getTwitchChannel(),
                userId = action.getUserId(),
                userName = action.getUserName()
            ))
            return

        now = datetime.now(timezone.utc)

        if state.getEndTime() < now:
            await self.__eventQueue.put(OutOfTimeCheckAnswerTriviaEvent(
                answer = action.getAnswer(),
                twitchChannel = action.getTwitchChannel(),
                userId = action.getUserId(),
                userName = action.getUserName()
            ))
            return

        if not await self.__checkAnswer(action.getAnswer(), state.getTriviaQuestion()):
            triviaScoreResult = await self.__triviaScoreRepository.incrementTotalLosses(
                twitchChannel = action.getTwitchChannel(),
                userId = action.getUserId()
            )

            await self.__eventQueue.put(IncorrectAnswerTriviaEvent(
                triviaQuestion = state.getTriviaQuestion(),
                answer = action.getAnswer(),
                twitchChannel = action.getTwitchChannel(),
                userId = action.getUserId(),
                userName = action.getUserName(),
                triviaScoreResult = triviaScoreResult
            ))
            return

        self.__states[action.getTwitchChannel().lower()] = None

        triviaScoreResult = await self.__triviaScoreRepository.incrementTotalWins(
            twitchChannel = action.getTwitchChannel(),
            userId = action.getUserId()
        )

        await self.__eventQueue.put(CorrectAnswerTriviaEvent(
            triviaQuestion = state.getTriviaQuestion(),
            pointsForWinning = state.getPointsForWinning(),
            answer = action.getAnswer(),
            userId = action.getUserId(),
            userName = action.getUserName(),
            triviaScoreResult = triviaScoreResult
        ))

    async def __handleActionStartNewGame(self, action: StartNewGameTriviaAction):
        if action is None:
            raise ValueError(f'action argument is malformed: \"{action}\"')
        elif action.getTriviaActionType() is not TriviaActionType.START_NEW_GAME:
            raise RuntimeError(f'TriviaActionType is not {TriviaActionType.START_NEW_GAME}: \"{action.getTriviaActionType()}\"')

        state = self.__states.get(action.getTwitchChannel().lower())
        now = datetime.now(timezone.utc)

        if state is not None and state.getEndTime() < now:
            await self.__eventQueue.put(GameAlreadyInProgressTriviaEvent(
                twitchChannel = action.getTwitchChannel(),
                userId = action.getUserId(),
                userName = action.getUserName()
            ))
            return

        triviaQuestion: AbsTriviaQuestion = None
        try:
            triviaQuestion = await self.__triviaRepository.fetchTrivia(
                twitchChannel = action.getTwitchChannel(),
                isJokeTriviaRepositoryEnabled = action.isJokeTriviaRepositoryEnabled()
            )
        except TooManyTriviaFetchAttemptsException as e:
            self.__timber.log('TriviaGameRepository', f'Reached limit on trivia fetch attempts without being able to successfully retrieve a question: {e}')

        if triviaQuestion is None:
            await self.__eventQueue.put(FailedToFetchQuestionTriviaEvent(
                twitchChannel = action.getTwitchChannel(),
                userId = action.getUserId(),
                userName = action.getUserName()
            ))
            return

        self.__states[action.getTwitchChannel().lower()] = TriviaGameState(
            triviaQuestion = triviaQuestion,
            pointsForWinning = action.getPointsForWinning(),
            secondsToLive = action.getSecondsToLive(),
            twitchChannel = action.getTwitchChannel(),
            userId = action.getUserId(),
            userName = action.getUserName()
        )

        await self.__eventQueue.put(NewGameTriviaEvent(
            triviaQuestion = triviaQuestion,
            pointsForWinning = action.getPointsForWinning(),
            secondsToLive = action.getSecondsToLive(),
            twitchChannel = action.getTwitchChannel(),
            userId = action.getUserId(),
            userName = action.getUserName()
        ))

    async def __refreshStatusOfLiveGames(self):
        if not utils.hasItems(self.__states):
            return

        now = datetime.now(timezone.utc)
        statesToRemove: List[TriviaGameState] = list()

        for state in self.__states.values():
            if state.getEndTime() < now:
                statesToRemove.append(state)

        if not utils.hasItems(statesToRemove):
            return

        for state in statesToRemove:
            self.__states[state.getTwitchChannel().lower()] = None

            triviaScoreResult = await self.__triviaScoreRepository.incrementTotalLosses(
                twitchChannel = state.getTwitchChannel(),
                userId = state.getUserId()
            )

            self.__eventQueue.put(OutOfTimeTriviaEvent(
                triviaQuestion = state.getTriviaQuestion(),
                twitchChannel = state.getTwitchChannel(),
                userId = state.getUserId(),
                userName = state.getUserName(),
                triviaScoreResult = triviaScoreResult
            ))

    def setEventListener(self, listener):
        self.__eventListener = listener

    async def __startActionLoop(self):
        while True:
            while not self.__actionQueue.empty():
                action = self.__actionQueue.get()

                if action.getTriviaActionType() is TriviaActionType.CHECK_ANSWER:
                    await self.__handleActionCheckAnswer(action)
                elif action.getTriviaActionType() is TriviaActionType.START_NEW_GAME:
                    await self.__handleActionStartNewGame(action)
                else:
                    raise UnknownTriviaActionTypeException(f'Unknown TriviaActionType: \"{action.getTriviaActionType()}\"')

            if utils.hasItems(self.__states):
                await self.__refreshStatusOfLiveGames()

            await asyncio.sleep(self.__sleepTimeSeconds)

    async def __startEventLoop(self):
        while True:
            eventListener = self.__eventListener

            if eventListener is not None:
                while not self.__eventQueue.empty():
                    event = self.__eventQueue.get()
                    await eventListener.onNewTriviaEvent(event)

            await asyncio.sleep(self.__sleepTimeSeconds)

    def submitAction(self, action: AbsTriviaAction):
        if action is None:
            raise ValueError(f'action argument is malformed: \"{action}\"')

        self.__actionQueue.put(action)

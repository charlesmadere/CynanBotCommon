import json
from typing import List, Optional, Set

try:
    import CynanBotCommon.utils as utils
    from CynanBotCommon.storage.backingDatabase import BackingDatabase
    from CynanBotCommon.storage.databaseConnection import DatabaseConnection
    from CynanBotCommon.storage.databaseType import DatabaseType
    from CynanBotCommon.timber.timberInterface import TimberInterface
    from CynanBotCommon.trivia.additionalTriviaAnswers import \
        AdditionalTriviaAnswers
    from CynanBotCommon.trivia.additionalTriviaAnswersRepositoryInterface import \
        AdditionalTriviaAnswersRepositoryInterface
    from CynanBotCommon.trivia.triviaExceptions import (
        AdditionalTriviaAnswerAlreadyExistsException,
        AdditionalTriviaAnswerIsMalformedException,
        AdditionalTriviaAnswerIsUnsupportedTriviaTypeException,
        TooManyAdditionalTriviaAnswersException)
    from CynanBotCommon.trivia.triviaSettingsRepository import \
        TriviaSettingsRepository
    from CynanBotCommon.trivia.triviaSource import TriviaSource
    from CynanBotCommon.trivia.triviaType import TriviaType
except:
    import utils
    from storage.backingDatabase import BackingDatabase
    from storage.databaseConnection import DatabaseConnection
    from storage.databaseType import DatabaseType
    from timber.timberInterface import TimberInterface
    from trivia.additionalTriviaAnswers import AdditionalTriviaAnswers
    from trivia.additionalTriviaAnswersRepositoryInterface import \
        AdditionalTriviaAnswersRepositoryInterface
    from trivia.triviaExceptions import (
        AdditionalTriviaAnswerAlreadyExistsException,
        AdditionalTriviaAnswerIsMalformedException,
        AdditionalTriviaAnswerIsUnsupportedTriviaTypeException,
        TooManyAdditionalTriviaAnswersException)
    from trivia.triviaSettingsRepository import TriviaSettingsRepository
    from trivia.triviaSource import TriviaSource
    from trivia.triviaType import TriviaType


class AdditionalTriviaAnswersRepository(AdditionalTriviaAnswersRepositoryInterface):

    def __init__(
        self,
        backingDatabase: BackingDatabase,
        timber: TimberInterface,
        triviaSettingsRepository: TriviaSettingsRepository
    ):
        if not isinstance(backingDatabase, BackingDatabase):
            raise ValueError(f'backingDatabase argument is malformed: \"{backingDatabase}\"')
        elif not isinstance(timber, TimberInterface):
            raise ValueError(f'timber argument is malformed: \"{timber}\"')
        elif not isinstance(triviaSettingsRepository, TriviaSettingsRepository):
            raise ValueError(f'triviaSettingsRepository argument is malformed: \"{triviaSettingsRepository}\"')

        self.__backingDatabase: BackingDatabase = backingDatabase
        self.__timber: TimberInterface = timber
        self.__triviaSettingsRepository: TriviaSettingsRepository = triviaSettingsRepository

        self.__isDatabaseReady: bool = False

    async def addAdditionalTriviaAnswer(
        self,
        additionalAnswer: str,
        triviaId: str,
        userId: str,
        triviaSource: TriviaSource,
        triviaType: TriviaType
    ) -> AdditionalTriviaAnswers:
        if not utils.isValidStr(additionalAnswer):
            raise AdditionalTriviaAnswerIsMalformedException(f'additionalAnswer argument is malformed: \"{additionalAnswer}\"')
        elif not utils.isValidStr(triviaId):
            raise ValueError(f'triviaId argument is malformed: \"{triviaId}\"')
        elif not utils.isValidStr(userId):
            raise ValueError(f'userId argument is malformed: \"{userId}\"')
        elif not isinstance(triviaSource, TriviaSource):
            raise ValueError(f'triviaSource argument is malformed: \"{triviaSource}\"')
        elif not isinstance(triviaType, TriviaType):
            raise ValueError(f'triviaType argument is malformed: \"{triviaType}\"')

        additionalAnswerLength = len(additionalAnswer)
        maxAdditionalTriviaAnswerLength = await self.__triviaSettingsRepository.getMaxAdditionalTriviaAnswerLength()

        if additionalAnswerLength > maxAdditionalTriviaAnswerLength:
            raise AdditionalTriviaAnswerIsMalformedException(f'Attempted to add additional answer \"{additionalAnswer}\" for {triviaSource.toStr()}:{triviaId}, but it is too long (len is {additionalAnswerLength}, max len is {maxAdditionalTriviaAnswerLength})')

        if triviaType is not TriviaType.QUESTION_ANSWER:
            raise AdditionalTriviaAnswerIsUnsupportedTriviaTypeException(
                message = f'Attempted to add additional answer \"{additionalAnswer}\" for {triviaSource.toStr()}:{triviaId}, but it is an unsupported type ({triviaType.toStr})',
                triviaSource = triviaSource,
                triviaType = triviaType
            )

        additionalAnswersSet: Set[str] = set()
        additionalAnswersSet.add(additionalAnswer)

        reference = await self.getAdditionalTriviaAnswers(
            triviaId = triviaId,
            triviaSource = triviaSource,
            triviaType = triviaType
        )

        if reference is not None:
            for existingAdditionalAnswer in reference.getAdditionalAnswers():
                if existingAdditionalAnswer.lower() == additionalAnswer.lower():
                    raise AdditionalTriviaAnswerAlreadyExistsException(f'Attempted to add additional answer \"{additionalAnswer}\" for {triviaSource.toStr()}:{triviaId}, but it already exists')

            additionalAnswersSet.update(reference.getAdditionalAnswers())

        additionalAnswersList: List[str] = list(additionalAnswersSet)
        additionalAnswersList.sort(key = lambda answer: answer.lower())

        if len(additionalAnswersList) > await self.__triviaSettingsRepository.getMaxAdditionalTriviaAnswers():
            raise TooManyAdditionalTriviaAnswersException(
                answers = additionalAnswersList,
                answerCount = len(additionalAnswersList)
            )

        additionalAnswersJson: str = json.dumps(additionalAnswersList)
        connection = await self.__getDatabaseConnection()

        if reference is None:
            await connection.execute(
                '''
                    INSERT INTO additionaltriviaanswers (additionalanswers, triviaid, triviasource, triviatype)
                    VALUES ($1, $2, $3, $4)
                ''',
                additionalAnswersJson, triviaId, triviaSource.toStr(), triviaType.toStr()
            )
        else:
            await connection.execute(
                '''
                    UPDATE additionaltriviaanswers
                    SET additionalanswers = $1
                    WHERE triviaid = $2 AND triviasource = $3 AND triviatype = $4
                ''',
                additionalAnswersJson, triviaId, triviaSource.toStr(), triviaType.toStr()
            )

        await connection.close()
        self.__timber.log('AdditionalTriviaAnswersRepository', f'Added additional answer (\"{additionalAnswer}\") for {triviaSource.toStr()}:{triviaId} (all answers: {additionalAnswersList})')

        return AdditionalTriviaAnswers(
            additionalAnswers = additionalAnswersList,
            triviaId = triviaId,
            triviaSource = triviaSource,
            triviaType = triviaType
        )

    async def deleteAdditionalTriviaAnswers(
        self,
        triviaId: str,
        triviaSource: TriviaSource,
        triviaType: TriviaType
    ) -> Optional[AdditionalTriviaAnswers]:
        if not utils.isValidStr(triviaId):
            raise ValueError(f'triviaId argument is malformed: \"{triviaId}\"')
        elif not isinstance(triviaSource, TriviaSource):
            raise ValueError(f'triviaSource argument is malformed: \"{triviaSource}\"')

        reference = await self.getAdditionalTriviaAnswers(
            triviaId = triviaId,
            triviaSource = triviaSource,
            triviaType = triviaType
        )

        if reference is None:
            self.__timber.log('AdditionalTriviaAnswersRepository', f'Attempted to delete additional answers for {triviaSource.toStr()}:{triviaId}, but there were none')
            return None

        connection = await self.__getDatabaseConnection()
        await connection.execute(
            '''
                DELETE FROM additionaltriviaanswers
                WHERE triviaid = $1 AND triviasource = $2 AND triviatype = $3
            ''',
            triviaId, triviaSource.toStr(), triviaType.toStr()
        )

        await connection.close()

        self.__timber.log('AdditionalTriviaAnswersRepository', f'Deleted additional answers for {triviaSource.toStr()}:{triviaId} (existing additional answers were {reference.getAdditionalAnswers()})')

        return reference

    async def getAdditionalTriviaAnswers(
        self,
        triviaId: str,
        triviaSource: TriviaSource,
        triviaType: TriviaType
    ) -> Optional[AdditionalTriviaAnswers]:
        if not utils.isValidStr(triviaId):
            raise ValueError(f'triviaId argument is malformed: \"{triviaId}\"')
        elif not isinstance(triviaSource, TriviaSource):
            raise ValueError(f'triviaSource argument is malformed: \"{triviaSource}\"')
        elif not isinstance(triviaType, TriviaType):
            raise ValueError(f'triviaType argument is malformed: \"{triviaType}\"')

        if not await self.__triviaSettingsRepository.areAdditionalTriviaAnswersEnabled():
            return None

        connection = await self.__getDatabaseConnection()
        record = await connection.fetchRow(
            '''
                SELECT additionalanswers FROM additionaltriviaanswers
                WHERE triviaid = $1 AND triviasource = $2 AND triviatype = $3
                LIMIT 1
            ''',
            triviaId, triviaSource.toStr(), triviaType.toStr()
        )

        await connection.close()

        if not utils.hasItems(record):
            return None

        additionalAnswersJson: Optional[str] = record[0]

        if not utils.isValidStr(additionalAnswersJson):
            return None

        additionalAnswersList: List[str] = json.loads(additionalAnswersJson)
        additionalAnswersList.sort(key = lambda answer: answer.lower())

        return AdditionalTriviaAnswers(
            additionalAnswers = additionalAnswersList,
            triviaId = triviaId,
            triviaSource = triviaSource,
            triviaType = triviaType
        )

    async def __getDatabaseConnection(self) -> DatabaseConnection:
        await self.__initDatabaseTable()
        return await self.__backingDatabase.getConnection()

    async def __initDatabaseTable(self):
        if self.__isDatabaseReady:
            return

        self.__isDatabaseReady = True
        connection = await self.__backingDatabase.getConnection()

        if connection.getDatabaseType() is DatabaseType.POSTGRESQL:
            await connection.createTableIfNotExists(
                '''
                    CREATE TABLE IF NOT EXISTS additionaltriviaanswers (
                        additionalanswers text,
                        triviaid public.citext NOT NULL,
                        triviasource public.citext NOT NULL,
                        triviatype public.citext NOT NULL,
                        PRIMARY KEY (triviaid, triviasource, triviatype)
                    )
                '''
            )
        elif connection.getDatabaseType() is DatabaseType.SQLITE:
            await connection.createTableIfNotExists(
                '''
                    CREATE TABLE IF NOT EXISTS additionaltriviaanswers (
                        additionalanswers TEXT,
                        triviaid TEXT NOT NULL COLLATE NOCASE,
                        triviasource TEXT NOT NULL COLLATE NOCASE,
                        triviatype TEXT NOT NULL COLLATE NOCASE,
                        PRIMARY KEY (triviaid, triviasource, triviatype)
                    )
                '''
            )
        else:
            raise RuntimeError(f'Encountered unexpected DatabaseType when trying to create tables: \"{connection.getDatabaseType()}\"')

        await connection.close()

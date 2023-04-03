import json
from typing import List, Optional, Set

try:
    import CynanBotCommon.utils as utils
    from CynanBotCommon.storage.backingDatabase import BackingDatabase
    from CynanBotCommon.storage.databaseConnection import DatabaseConnection
    from CynanBotCommon.storage.databaseType import DatabaseType
    from CynanBotCommon.timber.timber import Timber
    from CynanBotCommon.trivia.addTriviaAnswerResult import \
        AddTriviaAnswerResult
    from CynanBotCommon.trivia.triviaSettingsRepository import \
        TriviaSettingsRepository
    from CynanBotCommon.trivia.triviaSource import TriviaSource
except:
    import utils
    from storage.backingDatabase import BackingDatabase
    from storage.databaseConnection import DatabaseConnection
    from storage.databaseType import DatabaseType
    from timber.timber import Timber
    from trivia.addTriviaAnswerResult import AddTriviaAnswerResult
    from trivia.triviaSettingsRepository import TriviaSettingsRepository
    from trivia.triviaSource import TriviaSource


class AdditionalTriviaAnswersRepository():

    def __init__(
        self,
        backingDatabase: BackingDatabase,
        triviaSettingsRepository: TriviaSettingsRepository,
        timber: Timber
    ):
        if not isinstance(backingDatabase, BackingDatabase):
            raise ValueError(f'backingDatabase argument is malformed: \"{backingDatabase}\"')
        elif not isinstance(timber, Timber):
            raise ValueError(f'timber argument is malformed: \"{timber}\"')
        elif not isinstance(triviaSettingsRepository, TriviaSettingsRepository):
            raise ValueError(f'triviaSettingsRepository argument is malformed: \"{triviaSettingsRepository}\"')

        self.__backingDatabase: BackingDatabase = backingDatabase
        self.__triviaSettingsRepository: TriviaSettingsRepository = triviaSettingsRepository
        self.__timber: Timber = timber

        self.__isDatabaseReady: bool = False

    async def addAdditionalTriviaAnswer(
        self,
        additionalAnswer: str,
        triviaId: str,
        triviaSource: TriviaSource
    ) -> AddTriviaAnswerResult:
        if not utils.isValidStr(additionalAnswer):
            raise ValueError(f'additionalAnswer argument is malformed: \"{additionalAnswer}\"')
        elif not utils.isValidStr(triviaId):
            raise ValueError(f'triviaId argument is malformed: \"{triviaId}\"')
        elif not isinstance(triviaSource, TriviaSource):
            raise ValueError(f'triviaSource argument is malformed: \"{triviaSource}\"')

        additionalAnswersSet: Set[str] = set()
        additionalAnswersSet.add(additionalAnswer)

        existingAdditionalAnswers = await self.getAdditionalTriviaAnswers(
            triviaId = triviaId,
            triviaSource = triviaSource
        )

        if utils.hasItems(existingAdditionalAnswers):
            additionalAnswersSet.update(existingAdditionalAnswers)

        additionalAnswersList: List[str] = list(additionalAnswersSet)
        additionalAnswersJson: str = json.dumps(additionalAnswersList)
        connection = await self.__getDatabaseConnection()

        if existingAdditionalAnswers is None:
            await connection.execute(
                '''
                    INSERT INTO additionalanswers (additionalanswers, triviaid, triviasource)
                    VALUES ($1, $2, $3)
                ''',
                additionalAnswersJson, triviaId, triviaSource.toStr()
            )
        else:
            await connection.execute(
                '''
                    UPDATE additionalanswers
                    SET additionalanswers = $1
                    WHERE triviaid = $2 AND triviasource = $3
                ''',
                additionalAnswersJson, triviaId, triviaSource
            )

        await connection.close()
        self.__timber.log('AdditionalTriviaAnswersRepository', f'Added additional answer (\"{additionalAnswer}\") for {triviaSource.toStr()}:{triviaId} (all answers: {additionalAnswersList})')

        return AddTriviaAnswerResult(
            additionalAnswers = additionalAnswersList,
            triviaId = triviaId,
            triviaSource = triviaSource
        )

    async def getAdditionalTriviaAnswers(
        self,
        triviaId: str,
        triviaSource: TriviaSource
    ) -> Optional[Set[str]]:
        if not utils.isValidStr(triviaId):
            raise ValueError(f'triviaId argument is malformed: \"{triviaId}\"')
        elif not isinstance(triviaSource, TriviaSource):
            raise ValueError(f'triviaSource argument is malformed: \"{triviaSource}\"')

        if not await self.__triviaSettingsRepository.areAdditionalAnswersEnabled():
            return None

        connection = await self.__getDatabaseConnection()
        record = await connection.fetchRow(
            '''
                SELECT additionalanswers FROM additionaltriviaanswers
                WHERE triviaid = $1 AND triviasource = $2
                LIMIT 1
            ''',
            triviaId, triviaSource.toStr()
        )

        if not utils.hasItems(record):
            await connection.close()
            return None

        additionalAnswersJson: Optional[str] = record[0]
        await connection.close()

        if not utils.isValidStr(additionalAnswersJson):
            return None

        additionalAnswersList = json.loads(additionalAnswersJson)
        return set(additionalAnswersList)

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
                        PRIMARY KEY (triviaid, triviasource)
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
                        PRIMARY KEY (triviaid, triviasource)
                    )
                '''
            )
        else:
            raise RuntimeError(f'Encountered unexpected DatabaseType when trying to create tables: \"{connection.getDatabaseType()}\"')

        await connection.close()

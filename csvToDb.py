import asyncio
import csv
import hashlib
import sqlite3
from typing import List, Optional, Set

try:
    import CynanBotCommon.utils as utils
    from CynanBotCommon.backgroundTaskHelper import BackgroundTaskHelper
    from CynanBotCommon.timber.timber import Timber
    from CynanBotCommon.trivia.bannedWordsRepository import \
        BannedWordsRepository
    from CynanBotCommon.trivia.triviaContentScanner import TriviaContentScanner
    from CynanBotCommon.trivia.triviaDifficulty import TriviaDifficulty
    from CynanBotCommon.trivia.triviaSettingsRepository import \
        TriviaSettingsRepository
    from CynanBotCommon.trivia.triviaType import TriviaType
except:
    import utils
    from backgroundTaskHelper import BackgroundTaskHelper
    from timber.timber import Timber
    from trivia.bannedWordsRepository import BannedWordsRepository
    from trivia.triviaContentScanner import TriviaContentScanner
    from trivia.triviaDifficulty import TriviaDifficulty
    from trivia.triviaSettingsRepository import TriviaSettingsRepository
    from trivia.triviaType import TriviaType


backgroundTaskHelper = BackgroundTaskHelper(eventLoop = asyncio.get_event_loop())
timber = Timber(backgroundTaskHelper = backgroundTaskHelper)
bannedWordsRepository = BannedWordsRepository(timber = timber)
triviaContentScanner = TriviaContentScanner(
    bannedWordsRepository = bannedWordsRepository,
    timber = timber,
    triviaSettingsRepository = TriviaSettingsRepository()
)

def readInCsvRows(fileName: str) -> List[List[str]]:
    if not utils.isValidStr(fileName):
        raise ValueError(f'fileName argument is malformed: \"{fileName}\"')

    bannedWords = bannedWordsRepository.getBannedWords()
    rows: List[List[str]] = list()

    with open(fileName) as file:
        reader = csv.reader(file, delimiter = ',')
        lineNumber: int = 0

        for row in reader:
            lineNumber = lineNumber + 1

            if not utils.hasItems(row):
                print(f'Row #{lineNumber} in \"{fileName}\" is null/empty: {row}')
                continue

            encounteredBannedWord = False

            for r in row:
                for bannedWord in bannedWords:
                    if bannedWord in r.lower():
                        encounteredBannedWord = True
                        break

                if encounteredBannedWord:
                    break

            if encounteredBannedWord:
                print(f'Row #{lineNumber} in \"{fileName}\" contains a banned word: {row}')
            else:
                rows.append(row)

    if not utils.hasItems(rows):
        raise RuntimeError(f'Unable to read in any rows from \"{fileName}\": {rows}')

    print(f'Read in {len(rows)} row(s) from \"{fileName}\"')
    return rows

def writeRowsToSqlite(databaseName: str, rows: List[List[str]]):
    if not utils.isValidStr(databaseName):
        raise ValueError(f'databaseName argument is malformed: \"{databaseName}\"')
    elif not utils.hasItems(rows):
        raise ValueError(f'rows argument is malformed: \"{rows}\"')

    connection = sqlite3.connect(databaseName)
    cursor = connection.cursor()
    questionIds: Set[str] = set()
    rowNumber: int = 0

    for row in rows:
        rowNumber = rowNumber + 1

        if not utils.hasItems(row):
            raise ValueError(f'Row #{rowNumber} is null/empty: {row}')

        originalQuestionId: str = utils.cleanStr(row[0])
        category: str = utils.cleanStr(row[1])
        question: str = utils.cleanStr(row[3])

        wrongAnswer1: Optional[str] = None
        wrongAnswer2: Optional[str] = None
        wrongAnswer3: Optional[str] = None
        correctAnswer: Optional[str] = None
        triviaType: Optional[TriviaType] = None

        try:
            if len(row) > 5:
                wrongAnswer1 = utils.cleanStr(row[4])
                wrongAnswer2 = utils.cleanStr(row[5])
                wrongAnswer3 = utils.cleanStr(row[6])
                correctAnswer = utils.cleanStr(row[7])
                triviaType = TriviaType.MULTIPLE_CHOICE
            elif len(row) == 5:
                correctAnswer = utils.cleanStr(row[4])
                triviaType = TriviaType.TRUE_FALSE
            else:
                raise ValueError(f'triviaType at row #{rowNumber} can\'t be determined: \"{triviaType}\"')
        except IndexError as e:
            raise ValueError(f'index error at row #{rowNumber}: {e}')

        difficultyInt: Optional[int] = None
        difficulty: TriviaDifficulty = TriviaDifficulty.UNKNOWN
        try:
            difficultyInt = int(row[2])
            difficulty = TriviaDifficulty.fromInt(difficultyInt)
        except ValueError as e:
            raise ValueError(f'difficultyInt at row #{rowNumber} is malformed: \"{difficultyInt}\": {e}')

        if not utils.isValidStr(originalQuestionId):
            raise ValueError(f'originalQuestionId at row #{rowNumber} is malformed: \"{originalQuestionId}\"')
        elif not utils.isValidStr(category):
            raise ValueError(f'category at row #{rowNumber} is malformed: \"{category}\"')
        elif not utils.isValidStr(question):
            raise ValueError(f'question at row #{rowNumber} is malformed: \"{question}\"')
        elif not utils.isValidStr(correctAnswer):
            raise ValueError(f'correctAnswer at row #{rowNumber} is malformed: \"{correctAnswer}\"')
        elif not isinstance(difficulty, TriviaDifficulty):
            raise ValueError(f'difficulty at row #{rowNumber} is malformed: \"{difficulty}\"')
        elif not isinstance(triviaType, TriviaType):
            raise ValueError(f'triviaType at row #{rowNumber} is malformed: \"{triviaType}\"')
        elif triviaType is TriviaType.MULTIPLE_CHOICE and (not utils.isValidStr(wrongAnswer1) or not utils.isValidStr(wrongAnswer2) or not utils.isValidStr(wrongAnswer3)):
            raise ValueError(f'triviaType {TriviaType.MULTIPLE_CHOICE} has malformed wrong answers (wrongAnswer1=\"{wrongAnswer1}\") (wrongAnswer2=\"{wrongAnswer2}\") (wrongAnswer3=\"{wrongAnswer3}\")')
        elif triviaType is TriviaType.TRUE_FALSE and not utils.isValidBool(utils.strictStrToBool(correctAnswer)):
            raise ValueError(f'triviaType {TriviaType.TRUE_FALSE} has malformed correct answer (correctAnswer=\"{correctAnswer}\")')

        questionId: str = f'{originalQuestionId}:{category}:{difficulty.toStr()}:{triviaType.toStr()}:{question}:{wrongAnswer1}:{wrongAnswer2}:{wrongAnswer3}:{correctAnswer}'
        questionId = hashlib.md5(questionId.encode('utf-8')).hexdigest()

        if not utils.isValidStr(questionId):
            raise ValueError(f'questionId at row #{rowNumber} is malformed: \"{questionId}\"')
        elif questionId in questionIds:
            raise RuntimeError(f'questionId at row #{rowNumber} has collision: \"{questionId}\"')

        questionIds.add(questionId)

        try:
            cursor.execute(
                '''
                    INSERT INTO tdQuestions (category, correctAnswer, difficulty, question, questionId, tdQuestionId, triviaType, wrongAnswer1, wrongAnswer2, wrongAnswer3)
                    VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)
                ''',
                ( category, correctAnswer, difficulty.toInt(), question, questionId, originalQuestionId, triviaType.toStr(), wrongAnswer1, wrongAnswer2, wrongAnswer3 )
            )
        except (sqlite3.IntegrityError, sqlite3.OperationalError) as e:
            raise RuntimeError(f'Unable to insert question into DB: {e}\ncategory=\"{category}\" correctAnswer=\"{correctAnswer}\" difficulty=\"{difficulty}\" question=\"{question}\" questionId=\"{questionId}\" originalQuestionId=\"{originalQuestionId}\" triviaType=\"{triviaType}\" wrongAnswer1=\"{wrongAnswer1}\" wrongAnswer2=\"{wrongAnswer2}\" wrongAnswer3=\"{wrongAnswer3}\": {e}')

    connection.commit()
    cursor.close()
    connection.close()

    print(f'Wrote {rowNumber} rows into \"{databaseName}\" database')


trueFalse = readInCsvRows('CynanBotCommon/trivia/Delivery_500_TrueFalse_523A.csv')
writeRowsToSqlite('CynanBotCommon/trivia/triviaDatabaseTriviaQuestionRepository.sqlite', trueFalse)

multipleChoice = readInCsvRows('CynanBotCommon/trivia/Delivery_2KMC_523A.csv')
writeRowsToSqlite('CynanBotCommon/trivia/triviaDatabaseTriviaQuestionRepository.sqlite', multipleChoice)

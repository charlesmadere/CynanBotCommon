import asyncio
import csv
import hashlib
import sqlite3
from typing import List, Optional, Set

try:
    import CynanBotCommon.utils as utils
    from CynanBotCommon.timber.timber import Timber
    from CynanBotCommon.trivia.bannedWords.bannedWordsRepository import \
        BannedWordsRepository
    from CynanBotCommon.trivia.triviaContentScanner import TriviaContentScanner
    from CynanBotCommon.trivia.triviaDifficulty import TriviaDifficulty
    from CynanBotCommon.trivia.triviaSettingsRepository import \
        TriviaSettingsRepository
    from CynanBotCommon.trivia.triviaType import TriviaType
except:
    import utils
    from timber.timber import Timber
    from trivia.bannedWords.bannedWordsRepository import BannedWordsRepository
    from trivia.triviaContentScanner import TriviaContentScanner
    from trivia.triviaDifficulty import TriviaDifficulty
    from trivia.triviaSettingsRepository import TriviaSettingsRepository
    from trivia.triviaType import TriviaType


timber = Timber(eventLoop = asyncio.get_event_loop())

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
                raise RuntimeError(f'Row #{lineNumber} in \"{fileName}\" contains a banned word: {row}')
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
        subCategory: str = utils.cleanStr(row[2])
        question: str = utils.cleanStr(row[4])
        correctAnswerIndex: int = int(row[9]) - 1

        response0: Optional[str] = None
        response1: Optional[str] = None
        response2: Optional[str] = None
        response3: Optional[str] = None
        questionType: Optional[TriviaType] = None

        try:
            if len(row) > 5:
                response0 = utils.cleanStr(row[5])
                response1 = utils.cleanStr(row[6])
                response2 = utils.cleanStr(row[7])
                response3 = utils.cleanStr(row[8])
                questionType = TriviaType.MULTIPLE_CHOICE
            elif len(row) == 5:
                questionType = TriviaType.TRUE_FALSE
            else:
                raise ValueError(f'triviaType at row #{rowNumber} can\'t be determined: \"{questionType}\"')
        except IndexError as e:
            raise ValueError(f'index error at row #{rowNumber}: {e}')

        difficulty: TriviaDifficulty = TriviaDifficulty.UNKNOWN
        try:
            difficulty = TriviaDifficulty.fromInt(int(row[3]))
        except ValueError as e:
            raise ValueError(f'difficulty at row #{rowNumber} is malformed: {row}: {e}')

        if not utils.isValidStr(originalQuestionId):
            raise ValueError(f'originalQuestionId at row #{rowNumber} is malformed: \"{originalQuestionId}\"')
        elif not utils.isValidStr(category):
            raise ValueError(f'category at row #{rowNumber} is malformed: \"{category}\"')
        elif not utils.isValidStr(subCategory):
            raise ValueError(f'subCategory at row #{rowNumber} is malformed: \"{subCategory}\"')
        elif not utils.isValidStr(question):
            raise ValueError(f'question at row #{rowNumber} is malformed: \"{question}\"')
        elif not utils.isValidInt(correctAnswerIndex) or correctAnswerIndex < 0 or correctAnswerIndex > 3:
            raise ValueError(f'correctAnswerIndex at row #{rowNumber} is malformed: \"{correctAnswerIndex}\"')
        elif not isinstance(difficulty, TriviaDifficulty):
            raise ValueError(f'difficulty at row #{rowNumber} is malformed: \"{difficulty}\"')
        elif not isinstance(questionType, TriviaType):
            raise ValueError(f'questionType at row #{rowNumber} is malformed: \"{questionType}\"')
        elif questionType is TriviaType.MULTIPLE_CHOICE and (not utils.isValidStr(response0) or not utils.isValidStr(response1) or not utils.isValidStr(response2) or not utils.isValidStr(response3)):
            raise ValueError(f'questionType {TriviaType.MULTIPLE_CHOICE} at row #{rowNumber} has malformed wrong answers (response0=\"{response0}\") (response1=\"{response1}\") (response2=\"{response2}\") (response3=\"{response3}\")')
        elif questionType is TriviaType.TRUE_FALSE:
            raise NotImplementedError(f'questionType {TriviaType.TRUE_FALSE} at row #{rowNumber} is not implemented yet')

        questionId: str = f'{originalQuestionId}:{category}:{difficulty.toStr()}:{questionType.toStr()}:{question}:{response0}:{response2}:{response3}:{correctAnswerIndex}'
        questionId = hashlib.md5(questionId.encode('utf-8')).hexdigest()

        if not utils.isValidStr(questionId):
            raise ValueError(f'questionId at row #{rowNumber} is malformed: \"{questionId}\"')
        elif questionId in questionIds:
            raise RuntimeError(f'questionId at row #{rowNumber} has collision: \"{questionId}\"')

        questionIds.add(questionId)

        try:
            cursor.execute(
                '''
                    INSERT INTO tqcQuestions (category, correctAnswerIndex, difficulty, originalQuestionId, question, questionId, questionType, response0, response1, response2, response3, subCategory)
                    VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12)
                ''',
                ( category, correctAnswerIndex, difficulty.toInt(), originalQuestionId, question, questionId, questionType.toStr(), response0, response1, response2, response3, subCategory )
            )
        except (sqlite3.IntegrityError, sqlite3.OperationalError) as e:
            raise RuntimeError(f'Unable to insert question into DB: {e}\ncategory=\"{category}\" correctAnswerIndex=\"{correctAnswerIndex}\" difficulty=\"{difficulty}\" question=\"{question}\" questionId=\"{questionId}\" originalQuestionId=\"{originalQuestionId}\" triviaType=\"{questionType}\" response0=\"{response0}\" response1=\"{response1}\" response2=\"{response2}\" response3=\"{response3}\": {e}')

    connection.commit()
    cursor.close()
    connection.close()

    print(f'Wrote {rowNumber} rows into \"{databaseName}\" database')


multipleChoice = readInCsvRows('CynanBotCommon/tqc.csv')
writeRowsToSqlite('CynanBotCommon/trivia/triviaQuestionCompanyTriviaQuestionRepository.sqlite', multipleChoice)

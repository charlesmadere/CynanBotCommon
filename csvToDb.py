import csv
import hashlib
import sqlite3
from typing import List, Optional, Set

try:
    import CynanBotCommon.utils as utils
except:
    import utils


def readInCsvRows(fileName: str) -> List[List[str]]:
    if not utils.isValidStr(fileName):
        raise ValueError(f'fileName argument is malformed: \"{fileName}\"')

    rows: List[List[str]] = list()

    with open(fileName) as file:
        reader = csv.reader(file, delimiter = ',')
        lineNumber: int = 0

        for row in reader:
            lineNumber = lineNumber + 1

            if not utils.hasItems(row):
                print(f'Row #{lineNumber} in \"{fileName}\" is null/empty: {row}')
                continue
            elif len(row) != 8:
                print(f'Row #{lineNumber} in \"{fileName}\" has incorrect length ({len(row)}): {row}')
                continue

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

        tdQuestionId: str = utils.cleanStr(row[0])
        category: str = utils.cleanStr(row[1])
        question: str = utils.cleanStr(row[3])
        wrongAnswer1: str = utils.cleanStr(row[4])
        wrongAnswer2: str = utils.cleanStr(row[5])
        wrongAnswer3: str = utils.cleanStr(row[6])
        correctAnswer: str = utils.cleanStr(row[7])

        try:
            difficulty: Optional[int] = int(row[2])
        except ValueError:
            pass

        if not utils.isValidStr(tdQuestionId):
            raise ValueError(f'tdQuestionId at row #{rowNumber} is malformed: \"{tdQuestionId}\"')
        elif not utils.isValidStr(category):
            raise ValueError(f'category at row #{rowNumber} is malformed: \"{category}\"')
        elif not utils.isValidNum(difficulty):
            raise ValueError(f'difficulty at row #{rowNumber} is malformed: \"{difficulty}\"')
        elif not utils.isValidStr(question):
            raise ValueError(f'question at row #{rowNumber} is malformed: \"{question}\"')
        elif not utils.isValidStr(wrongAnswer1):
            raise ValueError(f'wrongAnswer1 at row #{rowNumber} is malformed: \"{wrongAnswer1}\"')
        elif not utils.isValidStr(wrongAnswer2):
            raise ValueError(f'wrongAnswer2 at row #{rowNumber} is malformed: \"{wrongAnswer2}\"')
        elif not utils.isValidStr(wrongAnswer3):
            raise ValueError(f'wrongAnswer3 at row #{rowNumber} is malformed: \"{wrongAnswer3}\"')
        elif not utils.isValidStr(correctAnswer):
            raise ValueError(f'correctAnswer at row #{rowNumber} is malformed: \"{correctAnswer}\"')

        questionId: str = f'{tdQuestionId}:{category}:{difficulty}:{question}:{wrongAnswer1}:{wrongAnswer2}:{wrongAnswer3}:{correctAnswer}'
        questionId = hashlib.sha224(questionId.encode('utf-8')).hexdigest()

        if questionId in questionIds:
            raise RuntimeError(f'questionId collision: \"{questionId}\"')

        questionIds.add(questionId)

        try:
            cursor.execute(
                '''
                    INSERT INTO tdQuestions (category, correctAnswer, difficulty, question, questionId, tdQuestionId, wrongAnswer1, wrongAnswer2, wrongAnswer3)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''',
                ( category, correctAnswer, difficulty, question, questionId, tdQuestionId, wrongAnswer1, wrongAnswer2, wrongAnswer3 )
            )
        except sqlite3.IntegrityError as e:
            raise RuntimeError(f'Unable to insert question into DB: {e}\ncategory=\"{category}\" correctAnswer=\"{correctAnswer}\" difficulty=\"{difficulty}\" question=\"{question}\" questionId=\"{questionId}\" tdQuestionId=\"{tdQuestionId}\" wrongAnswer1=\"{wrongAnswer1}\" wrongAnswer2=\"{wrongAnswer2}\" wrongAnswer3=\"{wrongAnswer3}\"')

    connection.commit()
    cursor.close()
    connection.close()

    print(f'Wrote {rowNumber} rows into \"{databaseName}\" database')

basketball = readInCsvRows('CynanBotCommon/basketball.csv')
writeRowsToSqlite('CynanBotCommon/trivia/triviaDatabaseTriviaQuestionRepository.sqlite', basketball)

nineties = readInCsvRows('CynanBotCommon/90s.csv')
writeRowsToSqlite('CynanBotCommon/trivia/triviaDatabaseTriviaQuestionRepository.sqlite', nineties)

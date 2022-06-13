import hashlib
import json
import sqlite3
from typing import Dict, List

try:
    import CynanBotCommon.utils as utils
    from CynanBotCommon.trivia.triviaType import TriviaType
except:
    import utils
    from trivia.triviaType import TriviaType


class Entry():
    def __init__(self, fileName: str, category: str):
        self.fileName: str = fileName
        self.category: str = category

prefixDir: str = 'CynanBotCommon/categories'

entries: List[Entry] = [
    Entry(f'{prefixDir}/animals.json', 'Animals'),
    Entry(f'{prefixDir}/celebrities.json', 'Celebrities'),
    Entry(f'{prefixDir}/entertainment.json', 'Entertainment'),
    Entry(f'{prefixDir}/for-kids.json', 'For Kids'),
    Entry(f'{prefixDir}/general.json', 'General'),
    Entry(f'{prefixDir}/geography.json', 'Geography'),
    Entry(f'{prefixDir}/history.json', 'History'),
    Entry(f'{prefixDir}/hobbies.json', 'Hobbies'),
    Entry(f'{prefixDir}/humanities.json', 'Humanities'),
    Entry(f'{prefixDir}/literature.json', 'Literature'),
    Entry(f'{prefixDir}/movies.json', 'Movies'),
    Entry(f'{prefixDir}/music.json', 'Music'),
    Entry(f'{prefixDir}/newest.json', 'Newest'),
    Entry(f'{prefixDir}/people.json', 'People'),
    Entry(f'{prefixDir}/rated.json', 'Rated'),
    Entry(f'{prefixDir}/religion-faith.json', 'Religion & Faith'),
    Entry(f'{prefixDir}/science-technology.json', 'Science & Technology'),
    Entry(f'{prefixDir}/sports.json', 'Sports'),
    Entry(f'{prefixDir}/television.json', 'Television'),
    Entry(f'{prefixDir}/video-games.json', 'Video Games'),
    Entry(f'{prefixDir}/world.json', 'World')
]

connection = sqlite3.connect('CynanBotCommon/trivia/openTriviaQaTriviaQuestionDatabase.sqlite')
cursor = connection.cursor()

for entry in entries:
    with open(entry.fileName, 'r') as file:
        jsonContents = json.load(file)

        if not utils.hasItems(jsonContents):
            raise RuntimeError(f'bad jsonContents for \"{entry.fileName}\": {jsonContents}')

        for questionJson in jsonContents:
            if not isinstance(questionJson, Dict) or len(questionJson) == 0:
                raise ValueError(f'bad data: {questionJson}')

            question = utils.getStrFromDict(questionJson, 'question', clean = True)
            answer = utils.getStrFromDict(questionJson, 'answer', clean = True)
            choices: List[str] = questionJson.get('choices')

            if not utils.hasItems(choices):
                raise ValueError(f'bad data: {questionJson}')
            elif len(choices) != 2 and len(choices) != 4 or not utils.areValidStrs(choices):
                raise ValueError(f'weird \"choices\" field: {questionJson}')

            response1: str = utils.cleanStr(choices[0])
            response2: str = utils.cleanStr(choices[1])
            response3: str = None
            response4: str = None

            questionType: TriviaType = None

            if len(choices) == 2 and (answer.lower() == 'true' or answer.lower() == 'false') and ((response1.lower() == 'true' or response1.lower() == 'false') and (response2.lower() == 'true' or response2.lower() == 'false')):
                if question.endswith('?'):
                    raise ValueError(f'bad data: {questionJson}')

                response1 = None
                response2 = None
                questionType = TriviaType.TRUE_FALSE
            else:
                try:
                    response3 = utils.cleanStr(choices[2])
                    response4 = utils.cleanStr(choices[3])
                    questionType = TriviaType.MULTIPLE_CHOICE
                except IndexError:
                    print(questionJson)
                    newQuestion = utils.cleanStr(input('question: '))
                    if utils.isValidStr(newQuestion):
                        question = newQuestion
                    newAnswer = utils.cleanStr(input('answer: '))
                    if utils.isValidStr(newAnswer):
                        answer = newAnswer
                    response1 = utils.cleanStr(input('response1: '))
                    response2 = utils.cleanStr(input('response2: '))
                    questionType = TriviaType.TRUE_FALSE

            hashAlg = hashlib.new('md4')
            hashAlg.update(f'{entry.fileName}:{entry.category}:{question}:{questionType.toStr()}:{answer}:{response1}:{response2}:{response3}:{response4}'.encode('utf-8'))
            questionId: str = hashAlg.hexdigest()

            if questionType is TriviaType.TRUE_FALSE and (not utils.isValidStr(question) or not utils.isValidStr(answer) or not utils.isValidStr(questionId)):
                raise ValueError(f'bad data: {questionJson}')
            elif questionType is TriviaType.MULTIPLE_CHOICE and (not utils.isValidStr(question) or not utils.isValidStr(answer) or not utils.isValidStr(response1) or not utils.isValidStr(response2) or not utils.isValidStr(response3) or not utils.isValidStr(response4) or not utils.isValidStr(questionId)):
                raise ValueError(f'bad data: {questionJson}')
            elif questionType is None:
                raise ValueError(f'bad data: {questionJson}')

            cursor.execute(
                '''
                    INSERT INTO triviaQuestions (category, correctAnswer, question, questionId, questionType, response1, response2, response3, response4)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''',
                ( entry.category, answer, question, questionId, questionType.toStr(), response1, response2, response3, response4 )
            )

cursor.close()
connection.commit()
connection.close()

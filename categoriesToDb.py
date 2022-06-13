import hashlib
import json
import sqlite3
from typing import List


import utils


class Entry():
    def __init__(self, fileName: str, category: str):
        self.fileName: str = fileName
        self.category: str = category

prefixDir: str = 'CynanBotCommon/categories'

entries: List[Entry] = [
    Entry(f'{prefixDir}/animals.json', 'Animals'),
    Entry(f'{prefixDir}/brain-teasers.json', 'Brain Teasers'),
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

connection = sqlite3.connect('openTriviaQaTriviaQuestionDatabase.sqlite')
cursor = connection.cursor()

for entry in entries:
    with open(entry.fileName, 'r') as file:
        jsonContents = json.load(file)

        if jsonContents is None or len(jsonContents) == 0:
            raise RuntimeError(f'bad jsonContents for \"{entry.fileName}\": {jsonContents}')

        for questionJson in jsonContents:
            question = utils.getStrFromDict(questionJson, 'question', clean = True)
            answer = utils.getStrFromDict(questionJson, 'answer', clean = True)

            try:
                response1: str = utils.cleanStr(questionJson['choices'][0])
                response2: str = utils.cleanStr(questionJson['choices'][1])
                response3: str = utils.cleanStr(questionJson['choices'][2])
                response4: str = utils.cleanStr(questionJson['choices'][3])
            except:
                raise ValueError(f'bad data: {questionJson}')

            hashAlg = hashlib.new('md4')
            hashAlg.update(f'{entry.fileName}:{entry.category}:{question}:{answer}:{response1}:{response2}:{response3}:{response4}'.encode('utf-8'))
            questionId: str = hashAlg.hexdigest()

            if not utils.isValidStr(question) or not utils.isValidStr(answer) or not utils.isValidStr(response1) or not utils.isValidStr(response2) or not utils.isValidStr(response3) or not utils.isValidStr(response4) or not utils.isValidStr(questionId):
                raise ValueError(f'bad data: {questionJson}')

            cursor.execute(
                '''
                    INSERT INTO triviaQuestions (category, correctAnswer, question, response1, response2, response3, response4, triviaId)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''',
                ( entry.category, answer, question, response1, response2, response3, response4, questionId )
            )

cursor.close()
connection.commit()
connection.close()

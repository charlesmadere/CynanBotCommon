import hashlib
import json
import sqlite3
from typing import Dict, List, Set

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


def fixString(s: str):
    if not utils.isValidStr(s):
        return ''

    try:
        s = s.encode('latin1').decode('utf-8')
    except UnicodeDecodeError as e:
        print(f'UnicodeDecodeError when encoding/decoding \"{s}\": {e}')
    except UnicodeEncodeError as e:
        print(f'UnicodeEncodeError when encoding/decoding \"{s}\": {e}')

    return ' '.join(utils.getCleanedSplits(s))


prefixDir: str = 'CynanBotCommon/categories'

entries: List[Entry] = [
    Entry(f'{prefixDir}/animals.json', 'Animals'),
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

finalOutput: Dict[str, object] = dict()

for entry in entries:
    askedForUserInput: bool = False

    with open(entry.fileName, 'r') as file:
        jsonContents: List[Dict[str, object]] = json.load(file)
        file.close()

        if not utils.hasItems(jsonContents):
            raise RuntimeError(f'bad jsonContents for \"{entry.fileName}\": {jsonContents}')

        for index, questionJson in enumerate(jsonContents):
            if not isinstance(questionJson, Dict) or not utils.hasItems(questionJson):
                raise ValueError(f'bad data: {questionJson}')

            newCategory = fixString(utils.getStrFromDict(questionJson, 'newCategory', fallback = ''))
            questionId = fixString(utils.getStrFromDict(questionJson, 'questionId', fallback = ''))
            questionTypeStr = fixString(utils.getStrFromDict(questionJson, 'questionType', fallback = ''))

            if questionId in finalOutput:
                raise RuntimeError(f'duplicate questionId (\"{questionId}\"): {questionJson}')

            if utils.isValidStr(newCategory) and utils.isValidStr(questionId) and utils.isValidStr(questionTypeStr):
                finalOutput[questionId] = questionJson
                continue

            question = fixString(utils.getStrFromDict(questionJson, 'question'))
            answer = fixString(utils.getStrFromDict(questionJson, 'answer'))
            category = fixString(utils.getStrFromDict(questionJson, 'category'))
            choices: List[str] = questionJson.get('choices')

            if len(choices) != 2 and len(choices) != 4:
                raise ValueError(f'bad data: {questionJson}')

            response1: str = fixString(choices[0])
            response2: str = fixString(choices[1])
            response3: str = None
            response4: str = None
            questionType: TriviaType = None

            if answer.lower() == 'yes' or answer.lower() == 'no' or answer.lower() == 'true' or answer.lower() == 'false':
                questionType = TriviaType.TRUE_FALSE

                if (response1.lower() != 'yes' and response1.lower() != 'no' and response1.lower() != 'true' and response1.lower() != 'false') or (response2.lower() != 'yes' and response2.lower() != 'no' and response2.lower() != 'true' and response2.lower() != 'false'):
                    raise ValueError(f'bad data: {questionJson}')

                if question.endswith('?'):
                    askedForUserInput = True
                    print(f'======\n{questionJson}')
                    newQuestion = fixString(input('question: '))

                    if utils.isValidStr(newQuestion):
                        question = newQuestion

                if answer.lower() == 'yes':
                    answer = str(True).lower()
                elif answer.lower() == 'no':
                    answer = str(False).lower()

                if answer.lower() != 'true' and answer.lower() != 'false':
                    raise ValueError(f'bad data: {questionJson}')
            elif len(choices) == 4:
                questionType = TriviaType.MULTIPLE_CHOICE

                try:
                    response3 = fixString(choices[2])
                except UnicodeDecodeError as e:
                    raise ValueError(f'bad data (index 2): {questionJson} ({e})')
                try:
                    response4 = fixString(choices[3])
                except UnicodeDecodeError as e:
                    raise ValueError(f'bad data (index 3): {questionJson} ({e})')
            else:
                raise ValueError(f'bad data: {questionJson}')

            hashAlg = hashlib.md5(f'{entry.fileName}:{entry.category}:{question}:{questionType.toStr()}:{answer}:{response1}:{response2}:{response3}:{response4}'.encode('utf-8'))
            questionId: str = hashAlg.hexdigest()

            if not utils.isValidStr(questionId):
                raise RuntimeError(f'malformed questionId (\"{questionId}\"): {questionJson}')
            elif questionId in finalOutput:
                raise RuntimeError(f'duplicate questionId (\"{questionId}\"): {questionJson}')

            if questionType is TriviaType.TRUE_FALSE and (not utils.isValidStr(question) or not utils.isValidStr(answer) or not utils.isValidStr(questionId) or not (answer.lower() != 'true' or answer.lower() != 'false')):
                raise ValueError(f'bad data: {questionJson}')
            elif questionType is TriviaType.MULTIPLE_CHOICE and (not utils.isValidStr(question) or not utils.isValidStr(answer) or not utils.isValidStr(response1) or not utils.isValidStr(response2) or not utils.isValidStr(response3) or not utils.isValidStr(response4) or not utils.isValidStr(questionId)):
                raise ValueError(f'bad data: {questionJson}')
            elif questionType is None:
                raise ValueError(f'bad data: {questionJson}')

            questionJson['answer'] = answer
            questionJson['category'] = category
            questionJson['newCategory'] = entry.category
            questionJson['question'] = question
            questionJson['questionId'] = questionId
            questionJson['questionType'] = questionType.toStr()

            if questionType is TriviaType.MULTIPLE_CHOICE:
                questionJson['choices'] = [ response1, response2, response3, response4 ]
            elif questionType is TriviaType.TRUE_FALSE:
                if 'choices' in questionJson:
                    del questionJson['choices']
            else:
                raise ValueError(f'bad data: {questionJson}')

            finalOutput[questionId ] = questionJson
            jsonContents[index] = questionJson

            with open(entry.fileName, 'w') as file:
                json.dump(jsonContents, file, indent = 2, sort_keys = True)

            print(f'Updated \"{entry.fileName}\": {questionJson}')

    if askedForUserInput:
        exit()

bannedWords: List[str] = [ 'potter', 'harry potter', 'hermione granger', 'rowling', 'albus', 'dumbledore', 'severus snape', 'snape', 'hogwarts', 'weasley', 'buckbeak', 'granger', 'muggle', 'sirius black', 'james potter', 'remus lupin', 'azkaban', 'hagrid', 'granger', 'lefty', 'leftist', 'male', 'female', 'gender', 'lacoste', 'trump', 'peeves', 'biden', 'obama', 'magic', 'liberal', 'blazing', 'blah' ]
bannedQuestionIds: Set[str] = set()

for questionJson in finalOutput:
    allStrs: List[str] = list()
    answer = questionJson['question']
    questionId = questionJson['questionId']
    allStrs.append(answer.lower())
    allStrs.append(questionJson['question'].lower())

    questionType = TriviaType.fromStr(questionJson['questionType'])
    if questionType is TriviaType.MULTIPLE_CHOICE:
        answerInChoices = False
        for choice in questionJson['choices']:
            allStrs.append(choice.lower())

            if answer == choice:
                answerInChoices = True

            if len(choice) >= 50:
                bannedQuestionIds.add(questionId)

        if not answerInChoices:
            bannedQuestionIds.add(questionId)

    for s in allStrs:
        for bannedWord in bannedWords:
            if bannedWord in s or len(s) >= 250:
                bannedQuestionIds.add(questionId)

for questionIdToRemove in bannedQuestionIds:
    print(f'Removing question: {finalOutput[questionIdToRemove]}')
    del finalOutput[questionIdToRemove]

# connection = sqlite3.connect('CynanBotCommon/trivia/openTriviaQaTriviaQuestionDatabase.sqlite')
# cursor = connection.cursor()

for questionJson in finalOutput:
    pass

# with open(outputFile, 'r') as file:
#     pass
    # cursor.execute(
    #     '''
    #         INSERT INTO triviaQuestions (category, correctAnswer, question, questionId, questionType, response1, response2, response3, response4)
    #         VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    #     ''',
    #     ( entry.category, answer, question, questionId, questionType.toStr(), response1, response2, response3, response4 )
    # )

# cursor.close()
# connection.commit()
# connection.close()

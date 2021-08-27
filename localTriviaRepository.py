import json
import random
from os import path
from typing import Dict

try:
    import CynanBotCommon.utils as utils
except:
    import utils


class LocalTriviaRepository():

    def __init__(
        self,
        localTriviaFile: str = 'CynanBotCommon/localTriviaFile.json'
    ):
        if not utils.isValidStr(localTriviaFile):
            raise ValueError(f'localTriviaFile argument is malformed: \"{localTriviaFile}\"')

        self.__localTriviaFile: str = localTriviaFile

    def __readJson(self) -> Dict:
        if not path.exists(self.__localTriviaFile):
            raise FileNotFoundError(f'Local Trivia file not found: \"{self.__localTriviaFile}\"')

        with open(self.__localTriviaFile, 'r') as file:
            jsonContents = json.load(file)

        if jsonContents is None:
            raise IOError(f'Error reading from Local Trivia file: \"{self.__localTriviaFile}\"')
        elif len(jsonContents) == 0:
            raise ValueError(f'JSON contents of Local Trivia file \"{self.__localTriviaFile}\" is empty')

        return jsonContents

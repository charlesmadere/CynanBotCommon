import json
import random
from os import path
from typing import Dict, List

try:
    import CynanBotCommon.utils as utils
except:
    import utils


class StarWarsQuotesRepository:

    def __init__(
        self,
        quotesFile: str = 'CynanBotCommon/starWarsQuotesRepository.json'
    ):
        if not utils.isValidStr(quotesFile):
            raise ValueError(f'quotesFile argument is malformed: \"{quotesFile}\"')

        self.__quotesFile = quotesFile

    def fetchRandomQuote(self) -> str:
        jsonContents = self.__getQuotes()
        randomIndex = random.randint(0, len(jsonContents) - 1)
        return jsonContents[randomIndex]

    def __getQuotes(self) -> List:
        jsonContents = self.__readJson()

        quotes = jsonContents.get("quotes")
        if not utils.hasItems(quotes):
            raise ValueError(f'JSON contents of quotes file \"{self.__quotesFile}\" is missing \"quotes\" key')

        return quotes

    def __readJson(self) -> Dict:
        if not path.exists(self.__quotesFile):
            raise FileNotFoundError(f'quotes file not found: \"{self.__quotesFile}\"')

        with open(self.__quotesFile, 'r') as file:
            jsonContents = json.load(file)

        if jsonContents is None:
            raise IOError(f'Error reading from quotes file: \"{self.__quotesFile}\"')
        elif len(jsonContents) == 0:
            raise ValueError(f'JSON contents of quotes file \"{self.__quotesFile}\" is empty')

        return jsonContents

    def searchQuote(self, query: str) -> str:
        if not utils.isValidStr(query):
            raise ValueError(f'query argument is malformed: \"{query}\"')

        query = utils.cleanStr(query)
        jsonContents = self.__getQuotes()

        for quote in jsonContents:
            if quote.lower().find(query.lower()) >= 0:
                return quote

        return None

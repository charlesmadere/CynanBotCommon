import random
import json
from os import path
from typing import Dict, List

class StarWars:
    def __init__(
        self,
        quotesFile: str = 'swQuotesRepository.json'
    ):
        self.__quotesFile = quotesFile

    def searchQuote(self, query) -> str:
        jsonContents = self.__getQuotes()

        for quote in jsonContents:
            if quote.lower().find(query.lower()) >= 0:
                return quote

        return "None"

    def fetchRandomQuote(self) -> str:
        jsonContents = self.__getQuotes()
        random_index = random.randint(0, len(jsonContents)-1)

        return jsonContents[random_index]

    def __getQuotes(self) -> List:
        jsonContents = self.__readJson()
        if "quotes" not in jsonContents:
            raise ValueError(f'JSON contents of quotes file \"{self.__quotesFile}\" is missing \"quotes\" key')
        quotes = jsonContents["quotes"]

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

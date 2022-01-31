import json
import random
import re
from os import path
from typing import Dict, List

try:
    import CynanBotCommon.utils as utils
except:
    import utils


class StarWarsQuotesRepository():

    def __init__(
        self,
        quotesFile: str = 'CynanBotCommon/starWars/starWarsQuotesRepository.json'
    ):
        if not utils.isValidStr(quotesFile):
            raise ValueError(f'quotesFile argument is malformed: \"{quotesFile}\"')

        self.__quotesFile: str = quotesFile
        self.__quoteInputRegEx = re.compile('\$\((.*)\)')

    def fetchRandomQuote(self, trilogy: str = None) -> str:
        jsonContents = self.__getQuotes(trilogy)
        quote = random.choice(jsonContents)
        return self.__processQuote(quote)

    def __getQuotes(self, trilogy: str = None) -> List[str]:
        trilogy = utils.cleanStr(trilogy)
        jsonContents = self.__readJson()

        quotes = jsonContents.get('quotes')
        if not utils.hasItems(quotes):
            raise ValueError(f'JSON contents of quotes file \"{self.__quotesFile}\" is missing \"quotes\" key')

        if utils.isValidStr(trilogy) and trilogy in quotes.keys():
            result = quotes[trilogy]
        else:
            result = [ item for sublist in quotes.values() for item in sublist ]

        return result

    def __processQuote(self, quote: str, input: str = None) -> str:
        result = self.__quoteInputRegEx.search(quote)
        if not result:
            return quote

        value = result.group(1)
        if utils.isValidStr(input):
            value = input

        return quote.replace(result.group(0), value)

    def __readJson(self) -> Dict[str, object]:
        if not path.exists(self.__quotesFile):
            raise FileNotFoundError(f'quotes file not found: \"{self.__quotesFile}\"')

        with open(self.__quotesFile, 'r') as file:
            jsonContents = json.load(file)

        if jsonContents is None:
            raise IOError(f'Error reading from quotes file: \"{self.__quotesFile}\"')
        elif len(jsonContents) == 0:
            raise ValueError(f'JSON contents of quotes file \"{self.__quotesFile}\" is empty')

        return jsonContents

    def searchQuote(self, query: str, input: str = None) -> str:
        if not utils.isValidStr(query):
            raise ValueError(f'query argument is malformed: \"{query}\"')

        query = utils.cleanStr(query)
        jsonContents = self.__getQuotes()

        for quote in jsonContents:
            if self.__processQuote(quote).lower().find(query.lower()) >= 0:
                return self.__processQuote(quote, input = input)

        return None

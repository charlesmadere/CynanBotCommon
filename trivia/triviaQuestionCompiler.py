import html
import re
from typing import List, Pattern, Set

try:
    import CynanBotCommon.utils as utils
except:
    import utils


class TriviaQuestionCompiler():

    def __init__(self):
        self.__ellipsisRegEx: Pattern = re.compile(r'(\.){3,}', re.IGNORECASE)
        self.__newLineRegEx: Pattern = re.compile(r'(\n)+', re.IGNORECASE)
        self.__tagRemovalRegEx: Pattern = re.compile(r'[<\[]\/?\w+[>\]]', re.IGNORECASE)
        self.__underscoreRegEx: Pattern = re.compile(r'_{2,}', re.IGNORECASE)
        self.__weirdEllipsisRegEx: Pattern = re.compile(r'\.\s\.\s\.', re.IGNORECASE)
        self.__whiteSpaceRegEx: Pattern = re.compile(r'\s{2,}', re.IGNORECASE)

    async def compileCategory(
        self,
        category: str,
        htmlUnescape: bool = False
    ) -> str:
        if not utils.isValidStr(category):
            raise ValueError(f'category argument is malformed: \"{category}\"')
        elif not utils.isValidBool(htmlUnescape):
            raise ValueError(f'htmlUnescape argument is malformed: \"{htmlUnescape}\"')

        return await self.__compileText(category, htmlUnescape)

    async def compileQuestion(
        self,
        question: str,
        htmlUnescape: bool = False
    ) -> str:
        if not utils.isValidStr(question):
            raise ValueError(f'question argument is malformed: \"{question}\"')
        elif not utils.isValidBool(htmlUnescape):
            raise ValueError(f'htmlUnescape argument is malformed: \"{htmlUnescape}\"')

        return await self.__compileText(question, htmlUnescape)

    async def compileResponse(
        self,
        response: str,
        htmlUnescape: bool = False
    ) -> str:
        if not utils.isValidStr(response):
            raise ValueError(f'response argument is malformed: \"{response}\"')
        elif not utils.isValidBool(htmlUnescape):
            raise ValueError(f'htmlUnescape argument is malformed: \"{htmlUnescape}\"')

        return await self.__compileText(response, htmlUnescape)

    async def compileResponses(
        self,
        responses: List[str],
        htmlUnescape: bool = False
    ) -> List[str]:
        if not utils.isValidBool(htmlUnescape):
            raise ValueError(f'htmlUnescape argument is malformed: \"{htmlUnescape}\"')

        if not utils.hasItems(responses):
            return list()

        compiledResponses: Set[str] = set()

        for response in responses:
            compiledResponse = await self.compileResponse(response, htmlUnescape)

            if utils.isValidStr(compiledResponse):
                compiledResponses.add(compiledResponse)

        return list(compiledResponses)

    async def __compileText(
        self,
        text: str,
        htmlUnescape: bool = False
    ) -> str:
        if not utils.isValidStr(text):
            raise ValueError(f'text argument is malformed: \"{text}\"')
        elif not utils.isValidBool(htmlUnescape):
            raise ValueError(f'htmlUnescape argument is malformed: \"{htmlUnescape}\"')

        text = text.strip()

        # replaces all "dot dot dot" sequences with the ellipsis character: "…"
        text = self.__ellipsisRegEx.sub('…', text).strip()

        # replaces all "dot space dot space dot" sequences with the ellipsis character
        text = self.__weirdEllipsisRegEx.sub('…', text).strip()

        # replaces all new line characters with 1 space
        text = self.__newLineRegEx.sub(' ', text).strip()

        # removes HTML tag-like junk
        text = self.__tagRemovalRegEx.sub('', text).strip()

        # replaces sequences of underscores (2 or more) with 3 underscores
        text = self.__underscoreRegEx.sub('___', text).strip()

        # replaces sequences of whitespace (2 or more) with 1 space
        text = self.__whiteSpaceRegEx.sub(' ', text).strip()

        if htmlUnescape:
            text = html.unescape(text)

        return text

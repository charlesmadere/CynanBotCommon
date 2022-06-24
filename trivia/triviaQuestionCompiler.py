import html
import re
from typing import Pattern

try:
    import CynanBotCommon.utils as utils
    from CynanBotCommon.trivia.triviaExceptions import \
        NoTriviaQuestionException
except:
    import utils

    from trivia.triviaExceptions import NoTriviaQuestionException


class TriviaQuestionCompiler():

    def __init__(self):
        self.__ellipsisRegEx: Pattern = re.compile(r'(\.){3,}', re.IGNORECASE)
        self.__newLineRegEx: Pattern = re.compile(r'(\n)*', re.IGNORECASE)
        self.__tagRemovalRegEx: Pattern = re.compile(r'<\/?\w+>', re.IGNORECASE)
        self.__underscoreRegEx: Pattern = re.compile(r'_{2,}', re.IGNORECASE)
        self.__whiteSpaceRegEx: Pattern = re.compile(r'\s{2,}', re.IGNORECASE)

    async def compileQuestion(
        self,
        question: str,
        htmlUnescape: bool = False
    ) -> str:
        if not utils.isValidStr(question):
            raise NoTriviaQuestionException(f'question argument is malformed: \"{question}\"')
        elif not utils.isValidBool(htmlUnescape):
            raise ValueError(f'htmlUnescape argument is malformed: \"{htmlUnescape}\"')

        question = question.strip()

        # replaces all "dot dot dot" sequences with the ellipsis character: "…"
        question = self.__ellipsisRegEx.sub('…', question).strip()

        # replaces all new line characters with 1 space
        question = self.__newLineRegEx.sub(' ', question).strip()

        # removes HTML tag-like junk
        question = self.__tagRemovalRegEx.sub('', question).strip()

        # replaces sequences of underscores (2 or more) with 3 underscores
        question = self.__underscoreRegEx.sub('___', question).strip()

        # replaces sequences of whitespace (2 or more) with 1 space
        question = self.__whiteSpaceRegEx.sub(' ', question).strip()

        if htmlUnescape:
            question = html.unescape(question)

        return question

import re
import uuid
from typing import Pattern

try:
    import CynanBotCommon.utils as utils
    from CynanBotCommon.cheerActions.cheerActionIdGeneratorInterface import \
        CheerActionIdGeneratorInterface
except:
    import utils
    from cheerActions.cheerActionIdGeneratorInterface import \
        CheerActionIdGeneratorInterface


class CheerActionIdGenerator(CheerActionIdGeneratorInterface):

    def __init__(self, maxLength: int = 3):
        if not utils.isValidInt(maxLength):
            raise ValueError(f'maxLength argument is malformed: \"{maxLength}\"')
        elif maxLength < 3 or maxLength > 8:
            raise ValueError(f'maxLength argument is out of bounds: {maxLength}')

        self.__maxLength: int = maxLength
        self.__actionIdRegEx: Pattern = re.compile(r'[^a-z0-9]', re.IGNORECASE)

    async def generateActionId(self) -> str:
        actionId = str(uuid.uuid4())
        return self.__actionIdRegEx.sub('', actionId)[:self.__maxLength]

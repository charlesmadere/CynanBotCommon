import hashlib
from typing import Optional

try:
    import CynanBotCommon.utils as utils
except:
    import utils


class TriviaIdGenerator():

    def __init__(self):
        pass

    async def generate(
        self,
        question: str,
        category: Optional[str] = None,
        difficulty: Optional[str] = None
    ) -> str:
        if not utils.isValidStr(question):
            raise ValueError(f'question argument is malformed: \"{question}\"')

        string = f'{question}'

        if utils.isValidStr(category):
            string = f'{string}:{category}'

        if utils.isValidStr(difficulty):
            string = f'{string}:{difficulty}'

        return hashlib.sha256(string.encode('utf-8')).hexdigest()

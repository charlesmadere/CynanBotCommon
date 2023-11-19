from typing import Any, Dict, Optional

try:
    import CynanBotCommon.utils as utils
except:
    import utils


class TwitchPaginationResponse():

    def __init__(self, cursor: Optional[str]):
        if not utils.isValidStr(cursor):
            raise ValueError(f'cursor argument is malformed: \"{cursor}\"')

        self.__cursor: str = cursor

    def getCursor(self) -> str:
        return self.__cursor

    def __repr__(self) -> str:
        dictionary = self.toDictionary()
        return str(dictionary)

    def toDictionary(self) -> Dict[str, Any]:
        return {
            'cursor': self.__cursor
        }

from typing import Any, Dict, Optional


class TwitchPaginationResponse():

    def __init__(self, cursor: Optional[str]):
        if cursor is not None and not isinstance(cursor, str):
            raise ValueError(f'cursor argument is malformed: \"{cursor}\"')

        self.__cursor: Optional[str] = cursor

    def getCursor(self) -> Optional[str]:
        return self.__cursor

    def __repr__(self) -> str:
        dictionary = self.toDictionary()
        return str(dictionary)

    def toDictionary(self) -> Dict[str, Any]:
        return {
            'cursor': self.__cursor
        }

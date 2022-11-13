from typing import Optional

try:
    import CynanBotCommon.utils as utils
    from CynanBotCommon.simpleDateTime import SimpleDateTime
except:
    import utils
    from simpleDateTime import SimpleDateTime


class TimberEntry():

    def __init__(self, tag: str, msg: str, exception: Optional[Exception] = None):
        if not utils.isValidStr(tag):
            raise ValueError(f'tag argument is malformed: \"{tag}\"')
        elif not utils.isValidStr(msg):
            raise ValueError(f'msg argument is malformed: \"{msg}\"')

        self.__tag: str = tag.strip()
        self.__msg: str = msg.strip()
        self.__exception: Optional[Exception] = exception

        self.__sdt: SimpleDateTime = SimpleDateTime()

    def getException(self) -> Optional[Exception]:
        return self.__exception

    def getMsg(self) -> str:
        return self.__msg

    def getSimpleDateTime(self) -> SimpleDateTime:
        return self.__sdt

    def getTag(self) -> str:
        return self.__tag

    def hasException(self) -> bool:
        return self.__exception is not None

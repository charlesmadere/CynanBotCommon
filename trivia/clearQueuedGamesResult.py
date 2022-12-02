import locale

try:
    import CynanBotCommon.utils as utils
except:
    import utils


class ClearQueuedGamesResult():

    def __init__(self, amountRemoved: int, oldQueueSize: int):
        if not utils.isValidNum(amountRemoved):
            raise ValueError(f'amountRemoved argument is malformed: \"{amountRemoved}\"')
        elif amountRemoved < 0:
            raise ValueError(f'amountRemoved argument is out of bounds: {amountRemoved}')
        elif not utils.isValidNum(oldQueueSize):
            raise ValueError(f'oldQueueSize argument is malformed: \"{oldQueueSize}\"')
        elif oldQueueSize < 0:
            raise ValueError(f'oldQueueSize argument is out of bounds: {oldQueueSize}')

        self.__amountRemoved: int = amountRemoved
        self.__oldQueueSize: int = oldQueueSize

    def getAmountRemoved(self) -> int:
        return self.__amountRemoved

    def getAmountRemovedStr(self) -> str:
        return locale.format_string("%d", self.__amountRemoved, grouping = True)

    def getOldQueueSize(self) -> int:
        return self.__oldQueueSize

    def getOldQueueSizeStr(self) -> str:
        return locale.format_string("%d", self.__oldQueueSize, grouping = True)

    def toStr(self) -> str:
        return f'amountRemoved={self.__amountRemoved}, oldQueueSize={self.__oldQueueSize}'

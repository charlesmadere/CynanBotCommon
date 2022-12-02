import locale

try:
    import CynanBotCommon.utils as utils
except:
    import utils


class AddQueuedGamesResult():

    def __init__(self, amountAdded: int, newQueueSize: int, oldQueueSize: int):
        if not utils.isValidNum(amountAdded):
            raise ValueError(f'amountAdded argument is malformed: \"{amountAdded}\"')
        elif amountAdded < 0:
            raise ValueError(f'amountAdded argument is out of bounds: {amountAdded}')
        elif not utils.isValidNum(newQueueSize):
            raise ValueError(f'newQueueSize argument is malformed: \"{newQueueSize}\"')
        elif newQueueSize < 0:
            raise ValueError(f'newQueueSize argument is out of bounds: {newQueueSize}')
        elif not utils.isValidNum(oldQueueSize):
            raise ValueError(f'oldQueueSize argument is malformed: \"{oldQueueSize}\"')
        elif oldQueueSize < 0:
            raise ValueError(f'oldQueueSize argument is out of bounds: {oldQueueSize}')

        self.__amountAdded: int = amountAdded
        self.__newQueueSize: int = newQueueSize
        self.__oldQueueSize: int = oldQueueSize

    def getAmountAdded(self) -> int:
        return self.__amountAdded

    def getAmountAddedStr(self) -> str:
        return locale.format_string("%d", self.__amountAdded, grouping = True)

    def getNewQueueSize(self) -> int:
        return self.__newQueueSize

    def getNewQueueSizeStr(self) -> str:
        return locale.format_string("%d", self.__newQueueSize, grouping = True)

    def getOldQueueSize(self) -> int:
        return self.__oldQueueSize

    def getOldQueueSizeStr(self) -> str:
        return locale.format_string("%d", self.__oldQueueSize, grouping = True)

    def toStr(self) -> str:
        return f'amountAdded={self.__amountAdded}, newQueueSize={self.__newQueueSize}, oldQueueSize={self.__oldQueueSize}'

try:
    import CynanBotCommon.utils as utils
    from CynanBotCommon.analogue.analogueProductType import AnalogueProductType
except:
    import utils

    from analogue.analogueProductType import AnalogueProductType


class AnalogueStoreEntry():

    def __init__(
        self,
        productType: AnalogueProductType,
        inStock: bool,
        name: str,
        price: str
    ):
        if productType is None:
            raise ValueError(f'productType argument is malformed: \"{productType}\"')
        elif not utils.isValidBool(inStock):
            raise ValueError(f'inStock argument is malformed: \"{inStock}\"')
        elif not utils.isValidStr(name):
            raise ValueError(f'name argument is malformed: \"{name}\"')

        self.__productType: AnalogueProductType = productType
        self.__inStock: bool = inStock
        self.__name: str = name
        self.__price: str = price

    def getName(self) -> str:
        return self.__name

    def getPrice(self) -> str:
        return self.__price

    def getProductType(self) -> AnalogueProductType:
        return self.__productType

    def hasPrice(self) -> bool:
        return utils.isValidStr(self.__price)

    def inStock(self) -> bool:
        return self.__inStock

    def toStr(self, includePrice: bool = False, includeStockInfo: bool = False) -> str:
        if not utils.isValidBool(includePrice):
            raise ValueError(f'includePrice argument is malformed: \"{includePrice}\"')
        elif not utils.isValidBool(includeStockInfo):
            raise ValueError(f'includeStockInfo argument is malformed: \"{includeStockInfo}\"')

        priceAndStockText = ''
        if includePrice or includeStockInfo:
            if includePrice and self.hasPrice():
                if includeStockInfo:
                    if self.inStock():
                        priceAndStockText = f' (in stock, {self.__price})'
                    else:
                        priceAndStockText = f' (out of stock, {self.__price})'
                else:
                    priceAndStockText = f' ({self.__price})'
            elif includeStockInfo:
                if self.inStock():
                    priceAndStockText = f' (in stock)'
                else:
                    priceAndStockText = f' (out of stock)'

        return f'{self.__name}{priceAndStockText}'

from typing import List

try:
    import CynanBotCommon.utils as utils
    from CynanBotCommon.analogue.analogueStoreEntry import AnalogueStoreEntry
except:
    import utils

    from analogue.analogueStoreEntry import AnalogueStoreEntry


class AnalogueStoreStock():

    def __init__(self, products: List[AnalogueStoreEntry]):
        if products is None:
            raise ValueError(f'products argument is malformed: \"{products}\"')

        self.__products: List[AnalogueStoreEntry] = products

    def getProducts(self) -> List[AnalogueStoreEntry]:
        return self.__products

    def hasProducts(self) -> bool:
        return utils.hasItems(self.__products)

    def toStr(self, includePrices: bool = False, inStockProductsOnly: bool = True, delimiter: str = ', ') -> str:
        if not utils.isValidBool(includePrices):
            raise ValueError(f'includePrices argument is malformed: \"{includePrices}\"')
        elif not utils.isValidBool(inStockProductsOnly):
            raise ValueError(f'inStockProductsOnly argument is malformed: \"{inStockProductsOnly}\"')
        elif delimiter is None:
            raise ValueError(f'delimiter argument is malformed: \"{delimiter}\"')

        if not self.hasProducts():
            return '🍃 Analogue store is empty'

        productStrings: List[str] = list()
        for product in self.__products:
            if inStockProductsOnly:
                if product.inStock():
                    productStrings.append(product.toStr(
                        includePrice = includePrices,
                        includeStockInfo = False
                    ))
            else:
                productStrings.append(product.toStr(
                    includePrice = includePrices,
                    includeStockInfo = True
                ))

        if inStockProductsOnly and not utils.hasItems(productStrings):
            return '🍃 Analogue store has nothing in stock'

        productsString = delimiter.join(productStrings)

        if inStockProductsOnly:
            return f'Analogue products in stock: {productsString}'
        else:
            return f'Analogue products: {productsString}'

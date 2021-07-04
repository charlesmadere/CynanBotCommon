from datetime import datetime, timedelta
from enum import Enum, auto
from typing import List

import requests
from lxml import html
from requests import ConnectionError, HTTPError, Timeout
from urllib3.exceptions import MaxRetryError, NewConnectionError

try:
    import CynanBotCommon.utils as utils
except:
    import utils


class AnalogueProductType(Enum):

    DAC = auto()
    DUO = auto()
    MEGA_SG = auto()
    NT_MINI = auto()
    OTHER = auto()
    POCKET = auto()
    SUPER_NT = auto()

    @classmethod
    def fromStr(cls, text: str):
        if not utils.isValidStr(text):
            return AnalogueProductType.OTHER

        text = text.lower()

        if 'dac' in text or 'dac' == text:
            return AnalogueProductType.DAC
        elif 'duo' in text or 'duo' == text:
            return AnalogueProductType.DUO
        elif 'mega sg -' in text or 'mega sg' == text:
            return AnalogueProductType.MEGA_SG
        elif 'nt mini' in text or 'nt mini' == text:
            return AnalogueProductType.NT_MINI
        elif 'pocket -' in text or 'pocket' == text:
            return AnalogueProductType.POCKET
        elif 'super nt -' in text or 'super nt' == text:
            return AnalogueProductType.SUPER_NT
        else:
            return AnalogueProductType.OTHER

    def toStr(self) -> str:
        if self is AnalogueProductType.DAC:
            return 'DAC'
        elif self is AnalogueProductType.DUO:
            return 'Duo'
        elif self is AnalogueProductType.MEGA_SG:
            return 'Mega Sg'
        elif self is AnalogueProductType.NT_MINI:
            return 'Nt mini'
        elif self is AnalogueProductType.OTHER:
            return 'other'
        elif self is AnalogueProductType.POCKET:
            return 'Pocket'
        elif self is AnalogueProductType.SUPER_NT:
            return 'Super Nt'
        else:
            raise RuntimeError(f'unknown AnalogueProductType: \"{self}\"')


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

        self.__productType = productType
        self.__inStock = inStock
        self.__name = name
        self.__price = price

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

        productStrings = list()
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


class AnalogueStoreRepository():

    def __init__(
        self,
        storeUrl: str = 'https://www.analogue.co/store',
        cacheTimeDelta: timedelta = timedelta(hours = 1)
    ):
        if not utils.isValidUrl(storeUrl):
            raise ValueError(f'storeUrl argument is malformed: \"{storeUrl}\"')
        elif cacheTimeDelta is None:
            raise ValueError(f'cacheTimeDelta argument is malformed: \"{cacheTimeDelta}\"')

        self.__storeUrl: str = storeUrl
        self.__cacheTime = datetime.utcnow() - cacheTimeDelta
        self.__cacheTimeDelta: timedelta = cacheTimeDelta
        self.__storeStock: AnalogueStoreStock = None

    def fetchStoreStock(self) -> AnalogueStoreStock:
        if self.__cacheTime + self.__cacheTimeDelta < datetime.utcnow() or self.__storeStock is None:
            self.__storeStock = self.__refreshStoreStock()
            self.__cacheTime = datetime.utcnow()

        return self.__storeStock

    def getStoreUrl(self) -> str:
        return self.__storeUrl

    def __refreshStoreStock(self) -> AnalogueStoreStock:
        print(f'Refreshing Analogue store stock... ({utils.getNowTimeText()})')

        rawResponse = None
        try:
            rawResponse = requests.get(url = self.__storeUrl, timeout = utils.getDefaultTimeout())
        except (ConnectionError, HTTPError, MaxRetryError, NewConnectionError, Timeout) as e:
            print(f'Exception occurred when attempting to fetch Analogue store stock: {e}')
            raise RuntimeError(f'Exception occurred when attempting to fetch Analogue store stock: {e}')

        htmlTree = html.fromstring(rawResponse.content)
        if htmlTree is None:
            print(f'Analogue store\'s htmlTree is malformed: \"{htmlTree}\"')
            raise ValueError(f'Analogue store\'s htmlTree is malformed: \"{htmlTree}\"')

        productTrees = htmlTree.find_class('store_product-header__1rLY-')
        if not utils.hasItems(productTrees):
            print(f'Analogue store\'s productTrees list is malformed: \"{productTrees}\"')
            raise ValueError(f'Analogue store\'s productTrees list is malformed: \"{productTrees}\"')

        products = list()

        for productTree in productTrees:
            productTrees = productTree.find_class('store_title__3eCzb')
            if productTrees is None or len(productTrees) != 1:
                continue

            nameAndPrice = utils.cleanStr(productTrees[0].text_content())
            if len(nameAndPrice) == 0:
                continue
            elif '8BitDo'.lower() in nameAndPrice.lower():
                # don't show 8BitDo products in the final stock listing
                continue

            name = None
            price = None
            indexOfDollar = nameAndPrice.find('$')

            if indexOfDollar == -1:
                name = utils.cleanStr(nameAndPrice)
            else:
                name = utils.cleanStr(nameAndPrice[0:indexOfDollar])
                price = utils.cleanStr(nameAndPrice[indexOfDollar:len(nameAndPrice)])

            if name[len(name) - 1] == '1':
                name = name[0:len(name) - 1]

            productType = AnalogueProductType.fromStr(name)

            inStock = True
            outOfStockElement = productTree.find_class('button_Disabled__2CEbR')
            if utils.hasItems(outOfStockElement):
                inStock = False

            products.append(AnalogueStoreEntry(
                productType = productType,
                inStock = inStock,
                name = name,
                price = price
            ))

        return AnalogueStoreStock(products = products)

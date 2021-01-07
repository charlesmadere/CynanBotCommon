from datetime import datetime, timedelta
from enum import Enum
from typing import List

import requests
from lxml import html

import CynanBotCommon.utils as utils


class AnalogueProductType(Enum):
    DAC = 0
    DUO = 1
    MEGA_SG = 2
    NT_MINI = 3
    OTHER = 4
    POCKET = 5
    SUPER_NT = 6


class AnalogueStoreRepository():

    def __init__(
        self,
        storeUrl: str='https://www.analogue.co/store',
        cacheTimeDelta=timedelta(hours=1)
    ):
        if not utils.isValidUrl(storeUrl):
            raise ValueError(f'storeUrl argument is malformed: \"{storeUrl}\"')
        elif cacheTimeDelta is None:
            raise ValueError(f'cacheTimeDelta argument is malformed: \"{cacheTimeDelta}\"')

        self.__storeUrl = storeUrl
        self.__cacheTime = datetime.now() - cacheTimeDelta
        self.__cacheTimeDelta = cacheTimeDelta
        self.__storeStock = None

    def fetchStoreStock(self):
        if self.__cacheTime + self.__cacheTimeDelta < datetime.now() or self.__storeStock is None:
            self.__storeStock = self.__refreshStoreStock()
            self.__cacheTime = datetime.now()

        return self.__storeStock

    def getStoreUrl(self):
        return self.__storeUrl

    def __refreshStoreStock(self):
        print(f'Refreshing Analogue store stock... ({utils.getNowTimeText()})')
        rawResponse = requests.get(self.__storeUrl)
        htmlTree = html.fromstring(rawResponse.content)

        if htmlTree is None:
            print(f'htmlTree is malformed: {htmlTree}')
            return None

        productTrees = htmlTree.find_class('store_product-header__1rLY-')

        if not utils.hasItems(productTrees):
            print(f'productTrees is malformed: {productTrees}')
            return None

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

            productType = AnalogueProductType.OTHER
            if 'dac' in name.lower():
                productType = AnalogueProductType.DAC
            elif 'duo' in name.lower():
                productType = AnalogueProductType.DUO
            elif 'mega sg -' in name.lower():
                productType = AnalogueProductType.MEGA_SG
            elif 'nt mini' in name.lower():
                productType = AnalogueProductType.NT_MINI
            elif 'pocket -' in name.lower():
                productType = AnalogueProductType.POCKET
            elif 'super nt -' in name.lower():
                productType = AnalogueProductType.SUPER_NT

            inStock = True
            outOfStockElement = productTree.find_class('button_Disabled__2CEbR')
            if utils.hasItems(outOfStockElement):
                inStock = False

            products.append(AnalogueStoreEntry(
                productType=productType,
                inStock=inStock,
                name=name,
                price=price
            ))

        return AnalogueStoreStock(
            products=products
        )


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
        elif inStock is None:
            raise ValueError(f'inStock argument is malformed: \"{inStock}\"')
        elif not utils.isValidStr(name):
            raise ValueError(f'name argument is malformed: \"{name}\"')

        self.__productType = productType
        self.__inStock = inStock
        self.__name = name
        self.__price = price

    def getName(self):
        return self.__name

    def getPrice(self):
        return self.__price

    def getProductType(self):
        return self.__productType

    def hasPrice(self):
        return utils.isValidStr(self.__price)

    def inStock(self):
        return self.__inStock

    def toStr(self, includePrice: bool = False, includeStockInfo: bool = False):
        if includePrice is None:
            raise ValueError(f'includePrice argument is malformed: \"{includePrice}\"')
        elif includeStockInfo is None:
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

    def __init__(self, products: List):
        if products == None:
            raise ValueError(f'products argument is malformed: \"{products}\"')

        self.__products = products

    def getProducts(self):
        return self.__products

    def hasProducts(self):
        return len(self.__products) >= 1

    def toStr(self, includePrices: bool = False, inStockProductsOnly: bool = True, delimiter: str = ', '):
        if includePrices is None:
            raise ValueError(f'includePrices argument is malformed: \"{includePrices}\"')
        elif inStockProductsOnly is None:
            raise ValueError(f'inStockProductsOnly argument is malformed: \"{inStockProductsOnly}\"')
        elif delimiter is None:
            raise ValueError(f'delimiter argument is malformed: \"{delimiter}\"')

        if not self.hasProducts():
            return '🍃 Analogue store is empty'

        productStrings = list()

        for product in self.__products:
            if inStockProductsOnly:
                if product.inStock():
                    productStrings.append(product.toStr(includePrice=includePrices, includeStockInfo=False))
            else:
                productStrings.append(product.toStr(includePrice=includePrices, includeStockInfo=True))

        if inStockProductsOnly and len(productStrings) == 0:
            return '🍃 Analogue store has nothing in stock'

        productsString = delimiter.join(productStrings)

        if inStockProductsOnly:
            return f'Analogue products in stock: {productsString}'
        else:
            return f'Analogue products: {productsString}'

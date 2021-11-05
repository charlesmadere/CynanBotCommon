from datetime import datetime, timedelta
from typing import List

import requests
from lxml import html
from requests import ConnectionError, HTTPError, Timeout
from requests.exceptions import ReadTimeout, TooManyRedirects
from urllib3.exceptions import MaxRetryError, NewConnectionError

try:
    import CynanBotCommon.utils as utils
    from CynanBotCommon.analogue.analogueProductType import AnalogueProductType
    from CynanBotCommon.analogue.analogueStoreEntry import AnalogueStoreEntry
    from CynanBotCommon.analogue.analogueStoreStock import AnalogueStoreStock
except:
    import utils

    from analogue.analogueProductType import AnalogueProductType
    from analogue.analogueStoreEntry import AnalogueStoreEntry
    from analogue.analogueStoreStock import AnalogueStoreStock


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
        except (ConnectionError, HTTPError, MaxRetryError, NewConnectionError, ReadTimeout, Timeout, TooManyRedirects) as e:
            print(f'Exception occurred when attempting to fetch Analogue store stock: {e}')
            raise RuntimeError(f'Exception occurred when attempting to fetch Analogue store stock: {e}')

        htmlTree = html.fromstring(rawResponse.content)
        if htmlTree is None:
            print(f'Analogue store\'s htmlTree is malformed: \"{htmlTree}\"')
            raise ValueError(f'Analogue store\'s htmlTree is malformed: \"{htmlTree}\"')

        productTrees = htmlTree.find_class('product-info')
        if not utils.hasItems(productTrees):
            print(f'Analogue store\'s productTrees list is malformed: \"{productTrees}\"')
            raise ValueError(f'Analogue store\'s productTrees list is malformed: \"{productTrees}\"')

        products: List[AnalogueStoreEntry] = list()

        for productTree in productTrees:
            productTrees = productTree.find_class('product-title')
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
            outOfStockElement = productTree.find_class('product-button button--disabled')
            if utils.hasItems(outOfStockElement):
                inStock = False

            products.append(AnalogueStoreEntry(
                productType = productType,
                inStock = inStock,
                name = name,
                price = price
            ))

        return AnalogueStoreStock(products = products)

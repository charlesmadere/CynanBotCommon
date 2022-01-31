from datetime import datetime, timedelta
from json.decoder import JSONDecodeError
from typing import Dict, List

import requests
from requests import ConnectionError, HTTPError, Timeout
from requests.exceptions import ReadTimeout, TooManyRedirects
from urllib3.exceptions import MaxRetryError, NewConnectionError

try:
    import CynanBotCommon.utils as utils
    from CynanBotCommon.timber.timber import Timber
except:
    import utils
    from timber.timber import Timber


class TamaleGuyStoreEntry():

    def __init__(
        self,
        enabled: bool,
        lowestInventory: int,
        totalInventory: int,
        name: str,
        price: str,
        productId: str
    ):
        if not utils.isValidBool(enabled):
            raise ValueError(f'enabled argument is malformed: \"{enabled}\"')
        elif not utils.isValidNum(lowestInventory):
            raise ValueError(f'lowestInventory argument is malformed: \"{lowestInventory}\"')
        elif not utils.isValidNum(totalInventory):
            raise ValueError(f'totalInventory argument is malformed: \"{totalInventory}\"')
        elif not utils.isValidStr(name):
            raise ValueError(f'name argument is malformed: \"{name}\"')
        elif not utils.isValidStr(price):
            raise ValueError(f'price argument is malformed: \"{price}\"')
        elif not utils.isValidStr(productId):
            raise ValueError(f'productId argument is malformed: \"{productId}\"')

        self.__enabled = enabled
        self.__lowestInventory = lowestInventory
        self.__totalInventory = totalInventory
        self.__name = name
        self.__price = price
        self.__productId = productId

    def getLowestInventory(self) -> int:
        return self.__lowestInventory

    def getName(self) -> str:
        return self.__name

    def getPrice(self) -> str:
        return self.__price

    def getProductId(self) -> str:
        return self.__productId

    def getTotalInventory(self) -> int:
        return self.__totalInventory

    def isEnabled(self) -> bool:
        return self.__enabled

    def toStr(self) -> str:
        return self.__name


class TamaleGuyStoreStock():

    def __init__(self, products: List[TamaleGuyStoreEntry]):
        if products is None:
            raise ValueError(f'products argument is malformed: \"{products}\"')

        self.__products = products

    def getProducts(self) -> List[TamaleGuyStoreEntry]:
        return self.__products

    def hasProducts(self) -> bool:
        return utils.hasItems(self.__products)

    def toStr(self, delimiter: str = ', ') -> str:
        if delimiter is None:
            raise ValueError(f'delimiter argument is malformed: \"{delimiter}\"')

        if not self.hasProducts():
            return '🍃 Tamale Guy store is empty'

        productStrings: List[str] = list()
        for product in self.__products:
            productStrings.append(product.toStr())

        productsString = delimiter.join(productStrings)
        return f'🫔 Tamale Guy products in stock: {productsString}'


class TamaleGuyRepository():

    def __init__(
        self,
        timber: Timber,
        cacheTimeDelta: timedelta = timedelta(hours = 1)
    ):
        if timber is None:
            raise ValueError(f'timber argument is malformed: \"{timber}\"')
        elif cacheTimeDelta is None:
            raise ValueError(f'cacheTimeDelta argument is malformed: \"{cacheTimeDelta}\"')

        self.__timber: Timber = timber
        self.__cacheTimeDelta: timedelta = cacheTimeDelta

        self.__cacheTime = datetime.utcnow() - cacheTimeDelta
        self.__storeStock: TamaleGuyStoreStock = None

    def fetchStoreStock(self) -> TamaleGuyStoreStock:
        if self.__cacheTime + self.__cacheTimeDelta < datetime.utcnow() or self.__storeStock is None:
            self.__storeStock = self.__refreshStoreStock()
            self.__cacheTime = datetime.utcnow()

        return self.__storeStock

    def __getProductsList(self, dataJson: List) -> List[TamaleGuyStoreEntry]:
        products: List[str] = list()

        if not utils.hasItems(dataJson):
            return products

        for productJson in dataJson:
            products.append(TamaleGuyStoreEntry(
                enabled = utils.getBoolFromDict(productJson['inventory'], 'enabled'),
                lowestInventory = utils.getIntFromDict(productJson['inventory'], 'lowest'),
                totalInventory = utils.getIntFromDict(productJson['inventory'], 'total'),
                name = utils.cleanStr(productJson['name']),
                price = utils.cleanStr(productJson['price']['regular_high_formatted']),
                productId = utils.cleanStr(productJson['id'])
            ))

        return products

    def __refreshStoreStock(self) -> TamaleGuyStoreStock:
        self.__timber.log('TamaleGuyRepository', f'Refreshing Tamale Guy store stock...')

        rawResponse = None
        try:
            rawResponse = requests.get(
                url = 'https://cdn4.editmysite.com/app/store/api/v13/editor/users/133185089/sites/894723485170061581/store-locations/11ead036057c3aa5b510ac1f6bbba828/products?page=1&per_page=200&include=images,categories&fulfillments[]=pickup',
                timeout = utils.getDefaultTimeout()
            )
        except (ConnectionError, HTTPError, MaxRetryError, NewConnectionError, ReadTimeout, Timeout, TooManyRedirects) as e:
            self.__timber.log('TamaleGuyRepository', f'Exception occurred when attempting to fetch Tamale Guy store stock: {e}')
            raise RuntimeError(f'Exception occurred when attempting to fetch Tamale Guy store stock: {e}')

        jsonResponse: Dict[str, object] = None
        try:
            jsonResponse = rawResponse.json()
        except JSONDecodeError as e:
            self.__timber.log('TamaleGuyRepository', f'Exception occurred when attempting to decode Tamale Guy store stock response into JSON: {e}')
            raise RuntimeError(f'Exception occurred when attempting to decode Tamale Guy store stock response into JSON: {e}')

        if 'data' not in jsonResponse:
            raise ValueError(f'JSON response for Tamale Guy store stock is missing the \"data\" field: {jsonResponse}')

        return TamaleGuyStoreStock(
            products = self.__getProductsList(jsonResponse['data'])
        )

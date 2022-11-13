from asyncio import TimeoutError
from datetime import datetime, timedelta, timezone
from typing import List, Optional

import aiohttp
from lxml import html

try:
    import CynanBotCommon.utils as utils
    from CynanBotCommon.analogue.analogueProductType import AnalogueProductType
    from CynanBotCommon.analogue.analogueStoreEntry import AnalogueStoreEntry
    from CynanBotCommon.analogue.analogueStoreStock import AnalogueStoreStock
    from CynanBotCommon.networkClientProvider import NetworkClientProvider
    from CynanBotCommon.timber.timber import Timber
except:
    import utils
    from networkClientProvider import NetworkClientProvider
    from timber.timber import Timber

    from analogue.analogueProductType import AnalogueProductType
    from analogue.analogueStoreEntry import AnalogueStoreEntry
    from analogue.analogueStoreStock import AnalogueStoreStock


class AnalogueStoreRepository():

    def __init__(
        self,
        networkClientProvider: NetworkClientProvider,
        timber: Timber,
        storeUrl: str = 'https://www.analogue.co/store',
        cacheTimeDelta: timedelta = timedelta(hours = 1)
    ):
        if networkClientProvider is None:
            raise ValueError(f'networkClientProvider argument is malformed: \"{networkClientProvider}\"')
        elif timber is None:
            raise ValueError(f'timber argument is malformed: \"{timber}\"')
        elif not utils.isValidUrl(storeUrl):
            raise ValueError(f'storeUrl argument is malformed: \"{storeUrl}\"')
        elif cacheTimeDelta is None:
            raise ValueError(f'cacheTimeDelta argument is malformed: \"{cacheTimeDelta}\"')

        self.__networkClientProvider: NetworkClientProvider = networkClientProvider
        self.__timber: Timber = timber
        self.__storeUrl: str = storeUrl
        self.__cacheTimeDelta: timedelta = cacheTimeDelta

        self.__cacheTime = datetime.now(timezone.utc) - cacheTimeDelta
        self.__storeStock: AnalogueStoreStock = None

    async def __buildProduct(self, productTree) -> Optional[AnalogueStoreEntry]:
        if productTree is None:
            raise ValueError(f'productTree argument is malformed: \"{productTree}\"')

        productTrees = productTree.find_class('product-title')
        if productTrees is None or len(productTrees) != 1:
            return None

        nameAndPrice = utils.cleanStr(productTrees[0].text_content())
        if len(nameAndPrice) == 0:
            return None
        elif '8BitDo'.lower() in nameAndPrice.lower():
            # don't show 8BitDo products in the final stock listing
            return None

        name: str = None
        price: str = None
        indexOfDollar: int = nameAndPrice.find('$')

        if indexOfDollar == -1:
            name = utils.cleanStr(nameAndPrice)
        else:
            name = utils.cleanStr(nameAndPrice[0:indexOfDollar])
            price = utils.cleanStr(nameAndPrice[indexOfDollar:len(nameAndPrice)])

        if name[len(name) - 1] == '1':
            name = name[0:len(name) - 1]

        productType = AnalogueProductType.fromStr(name)

        inStock: bool = True
        outOfStockElement = productTree.find_class('product-button button--disabled')
        if utils.hasItems(outOfStockElement):
            inStock = False

        return AnalogueStoreEntry(
            productType = productType,
            inStock = inStock,
            name = name,
            price = price
        )

    async def clearCaches(self):
        self.__storeStock = None
        self.__timber.log('AnalogueStoreRepository', 'Caches cleared')

    async def fetchStoreStock(self) -> AnalogueStoreStock:
        if self.__cacheTime + self.__cacheTimeDelta < datetime.now(timezone.utc) or self.__storeStock is None:
            self.__storeStock = await self.__fetchStoreStock()
            self.__cacheTime = datetime.now(timezone.utc)

        return self.__storeStock

    async def __fetchStoreStock(self) -> AnalogueStoreStock:
        self.__timber.log('AnalogueStoreRepository', f'Fetching Analogue store stock...')

        clientSession = await self.__networkClientProvider.get()

        try:
            response = await clientSession.get(self.__storeUrl)
        except (aiohttp.ClientError, TimeoutError) as e:
            self.__timber.log('AnalogueStoreRepository', f'Encountered network error: {e}', e)
            raise RuntimeError(f'Encountered network error when fetching Analogue store stock: {e}')

        if response.status != 200:
            self.__timber.log('AnalogueStoreRepository', f'Encountered non-200 HTTP status code when fetching Analogue store stock: {response.status}')
            raise RuntimeError(f'Encountered non-200 HTTP status code when fetching Analogue store stock: {response.status}')

        htmlTree = html.fromstring(await response.read())
        response.close()

        if htmlTree is None:
            self.__timber.log('AnalogueStoreRepository', f'Analogue store\'s htmlTree is malformed: \"{htmlTree}\"')
            raise ValueError(f'Analogue store\'s htmlTree is malformed: \"{htmlTree}\"')

        productTrees = htmlTree.find_class('product-info')
        if not utils.hasItems(productTrees):
            self.__timber.log('AnalogueStoreRepository', f'Analogue store\'s productTrees list is malformed: \"{productTrees}\"')
            raise ValueError(f'Analogue store\'s productTrees list is malformed: \"{productTrees}\"')

        products: List[AnalogueStoreEntry] = list()

        for productTree in productTrees:
            product = await self.__buildProduct(productTree)

            if product is not None:
                products.append(product)

        return AnalogueStoreStock(products = products)

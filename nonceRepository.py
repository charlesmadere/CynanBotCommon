from typing import Dict

try:
    import CynanBotCommon.utils as utils
    from CynanBotCommon.timber.timber import Timber
except:
    import utils
    from timber.timber import Timber


class NonceRepository():

    def __init__(
        self,
        timber: Timber
    ):
        if timber is None:
            raise ValueError(f'timber argument is malformed: \"{timber}\"')

        self.__cache: Dict[str, str] = dict()
        self.__timber: Timber = timber

    def getNonce(self, key: str) -> str:
        if not utils.isValidStr(key):
            raise ValueError(f'key argument is malformed: \"{key}\"')

        key = key.lower()
        return self.__cache.get(key)

    def setNonce(self, key: str, nonce: str):
        if not utils.isValidStr(key):
            raise ValueError(f'key argument is malformed: \"{key}\"')

        if utils.isValidStr(nonce):
            key = key.lower()
            self.__cache[key] = nonce
        else:
            self.__timber.log('NonceRepository', f'key \"{key}\" has an invalid nonce: \"{nonce}\"')
            self.__cache.pop(key, None)

from typing import Optional

try:
    import CynanBotCommon.utils as utils
    from CynanBotCommon.contentScanner.contentScannerInterface import \
        ContentScannerInterface
    from CynanBotCommon.timber.timberInterface import TimberInterface
except:
    import utils
    from contentScanner.contentScannerInterface import ContentScannerInterface
    from timber.timberInterface import TimberInterface


class ContentScanner(ContentScannerInterface):

    def __init__(
        self,
        timber: TimberInterface
    ):
        if not isinstance(timber, TimberInterface):
            raise ValueError(f'timber argument is malformed: \"{timber}\"')

        self.__timber: TimberInterface = timber

    async def scan(self, message: Optional[str]):
        if not utils.isValidStr(message):
            # TODO
            return

        # TODO
        pass

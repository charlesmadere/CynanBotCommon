from datetime import datetime, timezone
from typing import Dict

try:
    import CynanBotCommon.utils as utils
except:
    import utils


class WebsocketEvent():

    def __init__(self, eventData: Dict[str, object]):
        if not utils.hasItems(eventData):
            raise ValueError(f'eventData argument is malformed: \"{eventData}\"')

        self.__eventTime: datetime = datetime.now(timezone.utc)
        self.__eventData: Dict[str, object] = eventData

    def getEventData(self) -> Dict[str, object]:
        return self.__eventData

    def getEventTime(self) -> datetime:
        return self.__eventTime

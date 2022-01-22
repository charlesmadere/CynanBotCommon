from datetime import datetime
from typing import Dict

try:
    import CynanBotCommon.utils as utils
except:
    import utils


class WebsocketEvent():

    def __init__(
        self,
        eventData: Dict
    ):
        if not utils.hasItems(eventData):
            raise ValueError(f'eventData argument is malformed: \"{eventData}\"')

        self.__eventTime: datetime = datetime.utcnow()
        self.__eventData: Dict = eventData

    def getEventData(self) -> Dict:
        return self.__eventData

    def getEventTime(self):
        return self.__eventTime

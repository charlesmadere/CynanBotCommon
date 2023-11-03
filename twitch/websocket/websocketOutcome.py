from typing import List, Optional

try:
    import CynanBotCommon.utils as utils
    from CynanBotCommon.twitch.websocket.websocketOutcomeColor import \
        WebsocketOutcomeColor
    from CynanBotCommon.twitch.websocket.websocketOutcomePredictor import \
        WebsocketOutcomePredictor
except:
    import utils

    from twitch.websocket.websocketOutcomeColor import WebsocketOutcomeColor
    from twitch.websocket.websocketOutcomePredictor import \
        WebsocketOutcomePredictor


class WebsocketOutcome():

    def __init__(
        self,
        channelPoints: int,
        users: int,
        outcomeId: str,
        title: str,
        color: WebsocketOutcomeColor,
        topPredictors: Optional[List[WebsocketOutcomePredictor]] = None
    ):
        if not utils.isValidInt(channelPoints):
            raise ValueError(f'channelPoints argument is malformed: \"{channelPoints}\"')
        elif channelPoints < 0 or channelPoints > utils.getLongMaxSafeSize():
            raise ValueError(f'channelPoints argument is out of bounds: {channelPoints}')
        elif not utils.isValidInt(users):
            raise ValueError(f'users argument is malformed: \"{users}\"')
        elif users < 0 or users > utils.getIntMaxSafeSize():
            raise ValueError(f'users argument is out of bounds: {users}')
        elif not utils.isValidStr(outcomeId):
            raise ValueError(f'outcomeId argument is malformed: \"{outcomeId}\"')
        elif not utils.isValidStr(title):
            raise ValueError(f'title argument is malformed: \"{title}\"')
        elif not isinstance(color, WebsocketOutcomeColor):
            raise ValueError(f'color argument is malformed: \"{color}\"')
        elif topPredictors is not None and not isinstance(topPredictors, List):
            raise ValueError(f'topPredictors argument is malformed: \"{topPredictors}\"')

        self.__channelPoints: int = channelPoints
        self.__users: int = users
        self.__outcomeId: str = outcomeId
        self.__title: str = title
        self.__color: WebsocketOutcomeColor = color
        self.__topPredictors: Optional[List[WebsocketOutcomePredictor]] = topPredictors

    def getChannelPoints(self) -> int:
        return self.__channelPoints

    def getColor(self) -> WebsocketOutcomeColor:
        return self.__color

    def getOutcomeId(self) -> str:
        return self.__outcomeId

    def getTitle(self) -> str:
        return self.__title

    def getTopPredictors(self) -> Optional[List[WebsocketOutcomePredictor]]:
        return self.__topPredictors

    def getUsers(self) -> str:
        return self.__users

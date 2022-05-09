try:
    import CynanBotCommon.utils as utils
except:
    import utils


class UserRankResult():

    def __init__(
        self,
        jsonResponse
    ):
        # temporary
        self.jsonResponse = jsonResponse

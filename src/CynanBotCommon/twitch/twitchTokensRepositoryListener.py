from abc import ABC, abstractmethod

try:
    from CynanBotCommon.twitch.twitchTokensDetails import TwitchTokensDetails
except:
    from twitch.twitchTokensDetails import TwitchTokensDetails


class TwitchTokensRepositoryListener(ABC):

    @abstractmethod
    async def onUserAdded(self, tokensDetails: TwitchTokensDetails, twitchChannel: str):
        pass

    @abstractmethod
    async def onUserRemoved(self, twitchChannel: str):
        pass

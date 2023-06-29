try:
    from CynanBotCommon.twitch.twitchTokensDetails import TwitchTokensDetails
except:
    from twitch.twitchTokensDetails import TwitchTokensDetails


class TwitchTokensRepositoryListener():

    async def onUserAdded(self, tokensDetails: TwitchTokensDetails, twitchChannel: str):
        pass

    async def onUserRemoved(self, twitchChannel: str):
        pass

class TwitchCredentialsProviderInterface():

    async def getTwitchClientId(self) -> str:
        pass

    async def getTwitchClientSecret(self) -> str:
        pass

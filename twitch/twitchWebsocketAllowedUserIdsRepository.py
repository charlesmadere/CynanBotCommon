from typing import List

try:
    from CynanBotCommon.twitch.twitchWebsocketAllowedUserIdsRepositoryInterface import TwitchWebsocketAllowedUserIdsRepositoryInterface
except:
    from twitch.twitchWebsocketAllowedUserIdsRepositoryInterface import TwitchWebsocketAllowedUserIdsRepositoryInterface


class TwitchWebsocketAllowedUserIdsRepository(TwitchWebsocketAllowedUserIdsRepositoryInterface):

    async def getUserIds(self) -> List[str]:
        # TODO
        return list()

try:
    from ..websocket.twitchWebsocketUser import TwitchWebsocketUser
except:
    from twitch.websocket.twitchWebsocketUser import TwitchWebsocketUser


class TestTwitchWebsocketUser():

    def test_equals_withDifferentUserIds(self):
        userName = 'smCharles'

        user1 = TwitchWebsocketUser(
            twitchAccessToken = 'a',
            userId = '123',
            userName = userName
        )

        user2 = TwitchWebsocketUser(
            twitchAccessToken = 'z',
            userId = '456',
            userName = userName
        )

        assert user1 != user2

    def test_equals_withSameUserIds(self):
        userId = 'abc123'

        user1 = TwitchWebsocketUser(
            twitchAccessToken = 'a',
            userId = userId,
            userName = 'Anny'
        )

        user2 = TwitchWebsocketUser(
            twitchAccessToken = 'z',
            userId = userId,
            userName = 'Silvervale'
        )

        assert user1 == user2

    def test_hash_withDifferentUserIds(self):
        userName = 'Oatsngoats'

        user1 = TwitchWebsocketUser(
            twitchAccessToken = 'a',
            userId = '123',
            userName = userName
        )

        user2 = TwitchWebsocketUser(
            twitchAccessToken = 'z',
            userId = '456',
            userName = userName
        )

        assert hash(user1) != hash(user2)

    def test_hash_withSameUserIds(self):
        userId = 'abc123'

        user1 = TwitchWebsocketUser(
            twitchAccessToken = 'a',
            userId = userId,
            userName = 'imyt'
        )

        user2 = TwitchWebsocketUser(
            twitchAccessToken = 'z',
            userId = userId,
            userName = 'jay_cee'
        )

        assert hash(user1) == hash(user2)

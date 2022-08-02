import random
from typing import List, Optional

import emoji
from aiosqlite import Connection

try:
    import CynanBotCommon.utils as utils
    from CynanBotCommon.backingDatabase import BackingDatabase
except:
    import utils
    from backingDatabase import BackingDatabase


class TriviaEmoteGenerator():

    def __init__(
        self,
        backingDatabase: BackingDatabase
    ):
        if backingDatabase is None:
            raise ValueError(f'backingDatabase argument is malformed: \"{backingDatabase}\"')

        self.__backingDatabase: BackingDatabase = backingDatabase

        self.__isDatabaseReady: bool = False
        self.__emotes: List[str] = self.__createEmotesList()

    def __createEmotesList(self) -> List[str]:
        return [ '🏫', '🖍️', '✏️', '🧑‍🎓', '👨‍🎓', '👩‍🎓', '🧑‍🏫', '👨‍🏫', '👩‍🏫' ]

    async def getCurrentEmoteFor(self, twitchChannel: str) -> str:
        if not utils.isValidStr(twitchChannel):
            raise ValueError(f'twitchChannel argument is malformed: \"{twitchChannel}\"')

        emoteIndex = await self.__getCurrentEmoteIndexFor(twitchChannel)
        return self.__emotes[emoteIndex]

    async def __getCurrentEmoteIndexFor(self, twitchChannel: str) -> int:
        if not utils.isValidStr(twitchChannel):
            raise ValueError(f'twitchChannel argument is malformed: \"{twitchChannel}\"')

        connection = await self.__getDatabaseConnection()
        cursor = await connection.execute(
            '''
                SELECT emoteIndex FROM triviaEmotes
                WHERE twitchChannel = ?
                LIMIT 1
            ''',
            ( twitchChannel, )
        )

        row = await cursor.fetchone()
        emoteIndex: Optional[int] = None

        if row is not None:
            emoteIndex = row[0]

        await cursor.close()
        await connection.close()

        if not utils.isValidNum(emoteIndex) or emoteIndex < 0:
            emoteIndex = 0

        return emoteIndex

    async def __getDatabaseConnection(self) -> Connection:
        await self.__initDatabaseTable()
        return await self.__backingDatabase.getConnection()

    async def getNextEmoteFor(self, twitchChannel: str) -> str:
        if not utils.isValidStr(twitchChannel):
            raise ValueError(f'twitchChannel argument is malformed: \"{twitchChannel}\"')

        emoteIndex = await self.__getCurrentEmoteIndexFor(twitchChannel)
        emoteIndex = (emoteIndex + 1) % len(self.__emotes)

        connection = await self.__getDatabaseConnection()
        await connection.execute(
            '''
                INSERT INTO triviaEmotes (emoteIndex, twitchChannel)
                VALUES (?, ?)
                ON CONFLICT (twitchChannel) DO UPDATE SET emoteIndex = excluded.emoteIndex
            ''',
            ( emoteIndex, twitchChannel )
        )

        await connection.commit()
        await connection.close()

        return self.__emotes[emoteIndex]

    def getRandomEmote(self) -> str:
        return random.choice(self.__emotes)

    async def getValidatedAndNormalizedEmote(self, emote: Optional[str]) -> Optional[str]:
        if not utils.isValidStr(emote):
            return None
        elif not emoji.is_emoji(emote):
            return None

        try:
            emotesIndex = self.__emotes.index(emote)
            return self.__emotes[emotesIndex]
        except ValueError:
            # this exception can be safely ignored
            pass

        # transforms "👩‍🎓" into ":woman_student:"
        demojizedEmote: str = emoji.demojize(emote)
        if not utils.isValidStr(demojizedEmote):
            return None

        # removes the ending ":" character
        demojizedEmote = demojizedEmote[0:len(demojizedEmote) - 1]

        for e in self.__emotes:
            demojized = emoji.demojize(e)
            demojized = demojized[0:len(demojized) - 1]

            if demojizedEmote.startswith(demojized):
                return e

        return None

    async def __initDatabaseTable(self):
        if self.__isDatabaseReady:
            return

        self.__isDatabaseReady = True

        connection = await self.__backingDatabase.getConnection()
        cursor = await connection.execute(
            '''
                CREATE TABLE IF NOT EXISTS triviaEmotes (
                    emoteIndex INTEGER NOT NULL DEFAULT 0,
                    twitchChannel TEXT NOT NULL PRIMARY KEY COLLATE NOCASE
                )
            '''
        )

        await connection.commit()
        await cursor.close()
        await connection.close()

    async def isValidEmote(self, emote: Optional[str]) -> bool:
        if not utils.isValidStr(emote):
            return False

        return emote in self.__emotes

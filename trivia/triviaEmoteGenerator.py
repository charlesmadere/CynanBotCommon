import random
from collections import OrderedDict
from typing import Dict, List, Optional, Set

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
        self.__emotesDict: Dict[str, Optional[Set[str]]] = self.__createEmotesDict()
        self.__emotesList: List[str] = list(self.__emotesDict)

    def __createEmotesDict(self) -> Dict[str, Optional[Set[str]]]:
        emotesDict: Dict[str, Optional[Set[str]]] = OrderedDict()
        emotesDict['🧮'] = None
        emotesDict['👽'] = None
        emotesDict['🎒'] = None
        emotesDict['🍌'] = None
        emotesDict['📚'] = None
        emotesDict['🚌'] = None
        emotesDict['📇'] = None
        emotesDict['🖍️'] = None
        emotesDict['🧬'] = None
        emotesDict['🧐'] = None
        emotesDict['🍇'] = None
        emotesDict['🍏'] = None
        emotesDict['📒'] = None
        emotesDict['🍈'] = None
        emotesDict['🤓'] = None
        emotesDict['📓'] = None
        emotesDict['📎'] = None
        emotesDict['🍎'] = None
        emotesDict['📏'] = None
        emotesDict['✏️'] = None
        emotesDict['🏫'] = None
        emotesDict['🍊'] = None
        emotesDict['🤔'] = None
        emotesDict['💭'] = None
        emotesDict['📐'] = None
        emotesDict['🍉'] = None

        return emotesDict

    async def getCurrentEmoteFor(self, twitchChannel: str) -> str:
        if not utils.isValidStr(twitchChannel):
            raise ValueError(f'twitchChannel argument is malformed: \"{twitchChannel}\"')

        emoteIndex = await self.__getCurrentEmoteIndexFor(twitchChannel)
        return self.__emotesList[emoteIndex]

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
        emoteIndex = (emoteIndex + 1) % len(self.__emotesDict)

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

        return self.__emotesList[emoteIndex]

    def getRandomEmote(self) -> str:
        return random.choice(self.__emotesList)

    async def getValidatedAndNormalizedEmote(self, emote: Optional[str]) -> Optional[str]:
        if not utils.isValidStr(emote):
            return None
        elif not emoji.is_emoji(emote):
            return None

        if emote in self.__emotesDict:
            return emote

        for emoteKey, equivalentEmotes in self.__emotesDict.items():
            if utils.hasItems(equivalentEmotes):
                if emote in equivalentEmotes:
                    return emoteKey

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

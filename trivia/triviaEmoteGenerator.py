import random
from collections import OrderedDict
from typing import Dict, List, Optional, Set

try:
    import CynanBotCommon.utils as utils
    from CynanBotCommon.storage.backingDatabase import BackingDatabase
    from CynanBotCommon.storage.databaseConnection import DatabaseConnection
    from CynanBotCommon.storage.databaseType import DatabaseType
except:
    import utils
    from storage.backingDatabase import BackingDatabase
    from storage.databaseConnection import DatabaseConnection
    from storage.databaseType import DatabaseType


class TriviaEmoteGenerator():

    def __init__(
        self,
        backingDatabase: BackingDatabase
    ):
        if not isinstance(backingDatabase, BackingDatabase):
            raise ValueError(f'backingDatabase argument is malformed: \"{backingDatabase}\"')

        self.__backingDatabase: BackingDatabase = backingDatabase

        self.__isDatabaseReady: bool = False
        self.__emotesDict: Dict[str, Optional[Set[str]]] = self.__createEmotesDict()
        self.__emotesList: List[str] = list(self.__emotesDict)

    def __createEmotesDict(self) -> Dict[str, Optional[Set[str]]]:
        # Creates and returns a dictionary of emojis, with a set of emojis that should be
        # considered equivalent. For example: 👨‍🔬 (man scientist) and 👩‍🔬 (woman scientist)
        # should both be considered equivalents of the primary "root" 🧑‍🔬 (scientist) emoji.
        #
        # If a set is either None or empty, then the given emoji has no equivalent.

        emotesDict: Dict[str, Optional[Set[str]]] = OrderedDict()
        emotesDict['🧮'] = None
        emotesDict['⚗️'] = None
        emotesDict['👽'] = None
        emotesDict['🥓'] = None
        emotesDict['🎒'] = None
        emotesDict['🍌'] = None
        emotesDict['📊'] = None
        emotesDict['🫑'] = None
        emotesDict['🫐'] = None
        emotesDict['📚'] = None
        emotesDict['💼'] = None
        emotesDict['🚌'] = None
        emotesDict['📇'] = None
        emotesDict['🥕'] = None
        emotesDict['🧀'] = None
        emotesDict['🍒'] = None
        emotesDict['📋'] = None
        emotesDict['🦀'] = None
        emotesDict['🖍️'] = None
        emotesDict['🍛'] = None
        emotesDict['🧬'] = None
        emotesDict['🐬'] = None
        emotesDict['🐉'] = { '🐲' }
        emotesDict['🧐'] = None
        emotesDict['🚒'] = None
        emotesDict['🍇'] = None
        emotesDict['🍏'] = None
        emotesDict['🚁'] = None
        emotesDict['📒'] = None
        emotesDict['💡'] = None
        emotesDict['🍈'] = None
        emotesDict['🔬'] = None
        emotesDict['🍄'] = None
        emotesDict['🤓'] = None
        emotesDict['📓'] = None
        emotesDict['📎'] = None
        emotesDict['✏️'] = None
        emotesDict['🐧'] = None
        emotesDict['🍍'] = None
        emotesDict['🥔'] = None
        emotesDict['🍎'] = None
        emotesDict['🌈'] = None
        emotesDict['🍙'] = None
        emotesDict['🍠'] = None
        emotesDict['🚀'] = None
        emotesDict['🏫'] = None
        emotesDict['🦐'] = { '🍤' }
        emotesDict['🦑'] = { '🐙' }
        emotesDict['📏'] = None
        emotesDict['🍓'] = None
        emotesDict['🍊'] = None
        emotesDict['🔭'] = None
        emotesDict['🤔'] = None
        emotesDict['💭'] = None
        emotesDict['📐'] = None
        emotesDict['🌷'] = None
        emotesDict['🍉'] = None
        emotesDict['🐋'] = None

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
        record = await connection.fetchRow(
            '''
                SELECT emoteindex FROM triviaemotes
                WHERE twitchchannel = $1
                LIMIT 1
            ''',
            twitchChannel
        )

        emoteIndex: Optional[int] = None
        if utils.hasItems(record):
            emoteIndex = record[0]

        await connection.close()

        if not utils.isValidNum(emoteIndex) or emoteIndex < 0:
            emoteIndex = 0

        return emoteIndex

    async def __getDatabaseConnection(self) -> DatabaseConnection:
        await self.__initDatabaseTable()
        return await self.__backingDatabase.getConnection()

    async def getNextEmoteFor(self, twitchChannel: str) -> str:
        if not utils.isValidStr(twitchChannel):
            raise ValueError(f'twitchChannel argument is malformed: \"{twitchChannel}\"')

        emoteIndex = await self.__getCurrentEmoteIndexFor(twitchChannel)
        emoteIndex = (emoteIndex + 1) % len(self.__emotesList)

        connection = await self.__getDatabaseConnection()
        await connection.execute(
            '''
                INSERT INTO triviaemotes (emoteindex, twitchchannel)
                VALUES ($1, $2)
                ON CONFLICT (twitchchannel) DO UPDATE SET emoteindex = EXCLUDED.emoteindex
            ''',
            emoteIndex, twitchChannel
        )

        await connection.close()
        return self.__emotesList[emoteIndex]

    def getRandomEmote(self) -> str:
        return random.choice(self.__emotesList)

    async def getValidatedAndNormalizedEmote(self, emote: Optional[str]) -> Optional[str]:
        if not utils.isValidStr(emote):
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

        if connection.getDatabaseType() is DatabaseType.POSTGRESQL:
            await connection.createTableIfNotExists(
                '''
                    CREATE TABLE IF NOT EXISTS triviaemotes (
                        emoteindex smallint DEFAULT 0 NOT NULL,
                        twitchchannel public.citext NOT NULL PRIMARY KEY
                    )
                '''
            )
        elif connection.getDatabaseType() is DatabaseType.SQLITE:
            await connection.createTableIfNotExists(
                '''
                    CREATE TABLE IF NOT EXISTS triviaemotes (
                        emoteindex INTEGER NOT NULL DEFAULT 0,
                        twitchchannel TEXT NOT NULL PRIMARY KEY COLLATE NOCASE
                    )
                '''
            )
        else:
            raise RuntimeError(f'Encountered unexpected DatabaseType when trying to create tables: \"{connection.getDatabaseType()}\"')

        await connection.close()

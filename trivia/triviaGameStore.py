from typing import List, Optional

try:
    import CynanBotCommon.utils as utils
    from CynanBotCommon.trivia.absTriviaGameState import AbsTriviaGameState
    from CynanBotCommon.trivia.superTriviaGameState import SuperTriviaGameState
    from CynanBotCommon.trivia.triviaGameState import TriviaGameState
    from CynanBotCommon.trivia.triviaGameType import TriviaGameType
except:
    import utils

    from trivia.absTriviaGameState import AbsTriviaGameState
    from trivia.superTriviaGameState import SuperTriviaGameState
    from trivia.triviaGameState import TriviaGameState
    from trivia.triviaGameType import TriviaGameType


class TriviaGameStore():

    def __init__(self):
        self.__gameStates: List[AbsTriviaGameState] = list()

    async def add(self, state: AbsTriviaGameState):
        if state is None:
            raise ValueError(f'state argument is malformed: \"{state}\"')

        self.__gameStates.append(state)

    async def __get(self, twitchChannel: str, gameType: TriviaGameType) -> Optional[AbsTriviaGameState]:
        if not utils.isValidStr(twitchChannel):
            raise ValueError(f'twitchChannel argument is malformed: \"{twitchChannel}\"')
        elif gameType is None:
            raise ValueError(f'gameType argument is malformed: \"{gameType}\"')

        twitchChannel = twitchChannel.lower()
        gameStates = await self.getAll()

        for state in gameStates:
            if twitchChannel == state.getTwitchChannel().lower() and gameType is state.getTriviaGameType():
                return state

        return None

    async def getAll(self) -> List[AbsTriviaGameState]:
        return utils.copyList(self.__gameStates)

    async def getNormalGame(self, twitchChannel: str) -> Optional[TriviaGameState]:
        if not utils.isValidStr(twitchChannel):
            raise ValueError(f'twitchChannel argument is malformed: \"{twitchChannel}\"')

        return await self.__get(twitchChannel, TriviaGameType.NORMAL)

    async def getSuperGame(self, twitchChannel: str) -> Optional[SuperTriviaGameState]:
        if not utils.isValidStr(twitchChannel):
            raise ValueError(f'twitchChannel argument is malformed: \"{twitchChannel}\"')

        return await self.__get(twitchChannel, TriviaGameType.SUPER)

    async def __remove(self, twitchChannel: str, gameType: TriviaGameType):
        if not utils.isValidStr(twitchChannel):
            raise ValueError(f'twitchChannel argument is malformed: \"{twitchChannel}\"')

        twitchChannel = twitchChannel.lower()

        for state in self.__gameStates:
            if twitchChannel == state.getTwitchChannel().lower() and gameType is state.getTriviaGameType():
                self.__gameStates.remove(state)
                return

    async def removeNormalGame(self, twitchChannel: str):
        if not utils.isValidStr(twitchChannel):
            raise ValueError(f'twitchChannel argument is malformed: \"{twitchChannel}\"')

        await self.__remove(twitchChannel, TriviaGameType.NORMAL)

    async def removeSuperGame(self, twitchChannel: str):
        if not utils.isValidStr(twitchChannel):
            raise ValueError(f'twitchChannel argument is malformed: \"{twitchChannel}\"')

        await self.__remove(twitchChannel, TriviaGameType.SUPER)

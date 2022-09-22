from typing import List, Optional

try:
    import CynanBotCommon.utils as utils
    from CynanBotCommon.trivia.absTriviaGameState import AbsTriviaGameState
    from CynanBotCommon.trivia.superTriviaGameState import SuperTriviaGameState
    from CynanBotCommon.trivia.triviaExceptions import \
        UnknownTriviaGameTypeException
    from CynanBotCommon.trivia.triviaGameState import TriviaGameState
    from CynanBotCommon.trivia.triviaGameType import TriviaGameType
except:
    import utils

    from trivia.absTriviaGameState import AbsTriviaGameState
    from trivia.superTriviaGameState import SuperTriviaGameState
    from trivia.triviaExceptions import UnknownTriviaGameTypeException
    from trivia.triviaGameState import TriviaGameState
    from trivia.triviaGameType import TriviaGameType


class TriviaGameStore():

    def __init__(self):
        self.__normalGameStates: List[TriviaGameState] = list()
        self.__superGameStates: List[SuperTriviaGameState] = list()

    async def add(self, state: AbsTriviaGameState):
        if state is None:
            raise ValueError(f'state argument is malformed: \"{state}\"')

        if state.getTriviaGameType() is TriviaGameType.NORMAL:
            await self.__addNormalGame(state)
        elif state.getTriviaGameType() is TriviaGameType.SUPER:
            await self.__addSuperGame(state)
        else:
            raise UnknownTriviaGameTypeException(f'Unknown TriviaGameType: \"{state.getTriviaGameType()}\"')

    async def __addNormalGame(self, state: TriviaGameState):
        if state is None:
            raise ValueError(f'state argument is malformed: \"{state}\"')

        self.__normalGameStates.append(state)

    async def __addSuperGame(self, state: SuperTriviaGameState):
        if state is None:
            raise ValueError(f'state argument is malformed: \"{state}\"')

        self.__superGameStates.append(state)

    async def getAll(self) -> List[AbsTriviaGameState]:
        normalGames = await self.getNormalGames()
        superGames = await self.getSuperGames()

        allGames: List[AbsTriviaGameState] = list()
        allGames.extend(normalGames)
        allGames.extend(superGames)

        return allGames

    async def getNormalGame(self, twitchChannel: str, userName: str) -> Optional[TriviaGameState]:
        if not utils.isValidStr(twitchChannel):
            raise ValueError(f'twitchChannel argument is malformed: \"{twitchChannel}\"')
        elif not utils.isValidStr(userName):
            raise ValueError(f'userName argument is malformed: \"{userName}\"')

        normalGames = await self.getNormalGames()
        twitchChannel = twitchChannel.lower()
        userName = userName.lower()

        for state in normalGames:
            if twitchChannel == state.getTwitchChannel().lower() and userName == state.getUserName().lower():
                return state

        return None

    async def getNormalGames(self) -> List[TriviaGameState]:
        return utils.copyList(self.__normalGameStates)

    async def getSuperGame(self, twitchChannel: str) -> Optional[SuperTriviaGameState]:
        if not utils.isValidStr(twitchChannel):
            raise ValueError(f'twitchChannel argument is malformed: \"{twitchChannel}\"')

        superGames = await self.getSuperGames()
        twitchChannel = twitchChannel.lower()

        for state in superGames:
            if twitchChannel == state.getTwitchChannel().lower():
                return state

        return None

    async def getSuperGames(self) -> List[SuperTriviaGameState]:
        return utils.copyList(self.__superGameStates)

    async def removeNormalGame(self, twitchChannel: str, userName: str) -> bool:
        if not utils.isValidStr(twitchChannel):
            raise ValueError(f'twitchChannel argument is malformed: \"{twitchChannel}\"')
        elif not utils.isValidStr(userName):
            raise ValueError(f'userName argument is malformed: \"{userName}\"')

        normalGames = await self.getNormalGames()
        twitchChannel = twitchChannel.lower()
        userName = userName.lower()

        for index, state in enumerate(normalGames):
            if twitchChannel == state.getTwitchChannel().lower() and userName == state.getUserName().lower():
                del self.__normalGameStates[state]
                return True

        return False

    async def removeSuperGame(self, twitchChannel: str) -> bool:
        if not utils.isValidStr(twitchChannel):
            raise ValueError(f'twitchChannel argument is malformed: \"{twitchChannel}\"')

        superGames = await self.getSuperGames()
        twitchChannel = twitchChannel.lower()

        for index, state in enumerate(superGames):
            if twitchChannel == state.getTwitchChannel().lower():
                del self.__superGameStates[index]
                return True

        return False

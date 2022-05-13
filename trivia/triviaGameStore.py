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
        self.__gameStates: List[AbsTriviaGameState] = list()

    async def add(self, state: AbsTriviaGameState):
        if state is None:
            raise ValueError(f'state argument is malformed: \"{state}\"')

        self.__gameStates.append(state)

    async def __get(self, twitchChannel: str, userName: str, gameType: TriviaGameType) -> Optional[AbsTriviaGameState]:
        if not utils.isValidStr(twitchChannel):
            raise ValueError(f'twitchChannel argument is malformed: \"{twitchChannel}\"')
        elif gameType is None:
            raise ValueError(f'gameType argument is malformed: \"{gameType}\"')

        twitchChannel = twitchChannel.lower()

        if utils.isValidStr(userName):
            userName = userName.lower()

        gameStates = await self.getAll()

        for state in gameStates:
            if twitchChannel == state.getTwitchChannel().lower() and gameType is state.getTriviaGameType():
                if gameType is TriviaGameType.NORMAL:
                    normalGameState: TriviaGameState = state

                    if userName == normalGameState.getUserName().lower():
                        return normalGameState
                elif gameType is TriviaGameType.SUPER:
                    superGameState: SuperTriviaGameState = state
                    return superGameState
                else:
                    raise UnknownTriviaGameTypeException(f'Unknown TriviaGameType (twitchChannel=\"{twitchChannel}\") (userName=\"{userName}\"): \"{state.getTriviaGameType()}\"')

        return None

    async def getAll(self) -> List[AbsTriviaGameState]:
        return utils.copyList(self.__gameStates)

    async def getNormalGame(self, twitchChannel: str, userName: str) -> Optional[TriviaGameState]:
        if not utils.isValidStr(twitchChannel):
            raise ValueError(f'twitchChannel argument is malformed: \"{twitchChannel}\"')
        elif not utils.isValidStr(userName):
            raise ValueError(f'userName argument is malformed: \"{userName}\"')

        return await self.__get(
            twitchChannel = twitchChannel,
            userName = userName,
            gameType = TriviaGameType.NORMAL
        )

    async def getSuperGame(self, twitchChannel: str) -> Optional[SuperTriviaGameState]:
        if not utils.isValidStr(twitchChannel):
            raise ValueError(f'twitchChannel argument is malformed: \"{twitchChannel}\"')

        return await self.__get(
            twitchChannel = twitchChannel,
            userName = None,
            gameType = TriviaGameType.SUPER
        )

    async def __remove(self, twitchChannel: str, userName: str, gameType: TriviaGameType) -> bool:
        if not utils.isValidStr(twitchChannel):
            raise ValueError(f'twitchChannel argument is malformed: \"{twitchChannel}\"')
        elif gameType is None:
            raise ValueError(f'gameType argument is malformed: \"{gameType}\"')

        twitchChannel = twitchChannel.lower()

        if utils.isValidStr(userName):
            userName = userName.lower()

        for state in self.__gameStates:
            if twitchChannel == state.getTwitchChannel().lower() and gameType is state.getTriviaGameType():
                if gameType is TriviaGameType.NORMAL:
                    normalGameState: TriviaGameState = state

                    if userName == normalGameState.getUserName().lower():
                        self.__gameStates.remove(state)
                        return True
                elif gameType is TriviaGameType.SUPER:
                    self.__gameStates.remove(state)
                    return True
                else:
                    raise UnknownTriviaGameTypeException(f'Unknown TriviaGameType (twitchChannel=\"{twitchChannel}\") (userName=\"{userName}\"): \"{state.getTriviaGameType()}\"')

        return False

    async def removeNormalGame(self, twitchChannel: str, userName: str) -> bool:
        if not utils.isValidStr(twitchChannel):
            raise ValueError(f'twitchChannel argument is malformed: \"{twitchChannel}\"')
        elif not utils.isValidStr(userName):
            raise ValueError(f'userName argument is malformed: \"{userName}\"')

        return await self.__remove(
            twitchChannel = twitchChannel,
            userName = userName,
            gameType = TriviaGameType.NORMAL
        )

    async def removeSuperGame(self, twitchChannel: str) -> bool:
        if not utils.isValidStr(twitchChannel):
            raise ValueError(f'twitchChannel argument is malformed: \"{twitchChannel}\"')

        return await self.__remove(
            twitchChannel = twitchChannel,
            userName = None,
            gameType = TriviaGameType.SUPER
        )

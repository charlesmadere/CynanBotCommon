from typing import Dict, List

try:
    import CynanBotCommon.utils as utils
    from CynanBotCommon.pkmn.pokepediaGeneration import PokepediaGeneration
    from CynanBotCommon.pkmn.pokepediaMoveGeneration import \
        PokepediaMoveGeneration
except:
    import utils

    from pkmn.pokepediaGeneration import PokepediaGeneration
    from pkmn.pokepediaMoveGeneration import PokepediaMoveGeneration


class PokepediaMove():

    def __init__(
        self,
        generationMoves: Dict[PokepediaGeneration, PokepediaMoveGeneration],
        moveId: int,
        description: str,
        name: str,
        rawName: str
    ):
        if not utils.hasItems(generationMoves):
            raise ValueError(f'generationMoves argument is malformed: \"{generationMoves}\"')
        elif not utils.isValidNum(moveId):
            raise ValueError(f'moveId argument is malformed: \"{moveId}\"')
        elif not utils.isValidStr(description):
            raise ValueError(f'description argument is malformed: \"{description}\"')
        elif not utils.isValidStr(name):
            raise ValueError(f'name argument is malformed: \"{name}\"')
        elif not utils.isValidStr(rawName):
            raise ValueError(f'rawName argument is malformed: \"{rawName}\"')

        self.__generationMoves: Dict[PokepediaGeneration, PokepediaMoveGeneration] = generationMoves
        self.__moveId: int = moveId
        self.__description: str = description
        self.__name: str = name
        self.__rawName: str = rawName

    def getDescription(self) -> str:
        return self.__description

    def getGenerationMoves(self) -> Dict[PokepediaGeneration, PokepediaMoveGeneration]:
        return self.__generationMoves

    def getMoveId(self) -> int:
        return self.__moveId

    def getName(self) -> str:
        return self.__name

    def getRawName(self) -> str:
        return self.__rawName

    def toStrList(self) -> List[str]:
        strings: List[str] = list()
        strings.append(f'{self.getName()} — {self.getDescription()}')

        for gen in PokepediaGeneration:
            if gen in self.__generationMoves:
                genMove = self.__generationMoves[gen]
                strings.append(genMove.toStr())

        return strings

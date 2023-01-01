from typing import Dict, List, Optional

try:
    import CynanBotCommon.utils as utils
    from CynanBotCommon.pkmn.pokepediaContestType import PokepediaContestType
    from CynanBotCommon.pkmn.pokepediaGeneration import PokepediaGeneration
    from CynanBotCommon.pkmn.pokepediaMachine import PokepediaMachine
    from CynanBotCommon.pkmn.pokepediaMoveGeneration import \
        PokepediaMoveGeneration
except:
    import utils

    from pkmn.pokepediaContestType import PokepediaContestType
    from pkmn.pokepediaGeneration import PokepediaGeneration
    from pkmn.pokepediaMachine import PokepediaMachine
    from pkmn.pokepediaMoveGeneration import PokepediaMoveGeneration


class PokepediaMove():

    def __init__(
        self,
        contestType: PokepediaContestType,
        generationMachines: Optional[Dict[PokepediaGeneration, List[PokepediaMachine]]],
        generationMoves: Dict[PokepediaGeneration, PokepediaMoveGeneration],
        moveId: int,
        initialGeneration: PokepediaGeneration,
        description: str,
        name: str,
        rawName: str
    ):
        if not isinstance(contestType, PokepediaContestType):
            raise ValueError(f'contestType argument is malformed: \"{contestType}\"')
        elif not utils.hasItems(generationMoves):
            raise ValueError(f'generationMoves argument is malformed: \"{generationMoves}\"')
        elif not utils.isValidInt(moveId):
            raise ValueError(f'moveId argument is malformed: \"{moveId}\"')
        elif not isinstance(initialGeneration, PokepediaGeneration):
            raise ValueError(f'initialGeneration argument is malformed: \"{initialGeneration}\"')
        elif not utils.isValidStr(description):
            raise ValueError(f'description argument is malformed: \"{description}\"')
        elif not utils.isValidStr(name):
            raise ValueError(f'name argument is malformed: \"{name}\"')
        elif not utils.isValidStr(rawName):
            raise ValueError(f'rawName argument is malformed: \"{rawName}\"')

        self.__contestType: PokepediaContestType = contestType
        self.__generationMachines: Optional[Dict[PokepediaGeneration, List[PokepediaMachine]]] = generationMachines
        self.__generationMoves: Dict[PokepediaGeneration, PokepediaMoveGeneration] = generationMoves
        self.__moveId: int = moveId
        self.__initialGeneration: PokepediaGeneration = initialGeneration
        self.__description: str = description
        self.__name: str = name
        self.__rawName: str = rawName

    def getContestType(self) -> PokepediaContestType:
        return self.__contestType

    def getDescription(self) -> str:
        return self.__description

    def getGenerationMachines(self) -> Optional[Dict[PokepediaGeneration, List[PokepediaMachine]]]:
        return self.__generationMachines

    def getGenerationMoves(self) -> Dict[PokepediaGeneration, PokepediaMoveGeneration]:
        return self.__generationMoves

    def getInitialGeneration(self) -> PokepediaGeneration:
        return self.__initialGeneration

    def getMoveId(self) -> int:
        return self.__moveId

    def getName(self) -> str:
        return self.__name

    def getRawName(self) -> str:
        return self.__rawName

    def hasMachines(self) -> bool:
        return utils.hasItems(self.__generationMachines)

    def toStrList(self) -> List[str]:
        strings: List[str] = list()
        strings.append(f'{self.getName()} — {self.getDescription()}')

        for gen in PokepediaGeneration:
            if gen in self.__generationMoves:
                genMove = self.__generationMoves[gen]
                strings.append(genMove.toStr())

        return strings

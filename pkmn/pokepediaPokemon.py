import locale
from typing import Dict, List

try:
    import CynanBotCommon.utils as utils
    from CynanBotCommon.pkmn.pokepediaDamageMultiplier import \
        PokepediaDamageMultiplier
    from CynanBotCommon.pkmn.pokepediaElementType import PokepediaElementType
    from CynanBotCommon.pkmn.pokepediaGeneration import PokepediaGeneration
    from CynanBotCommon.pkmn.pokepediaTypeChart import PokepediaTypeChart
except:
    import utils

    from pkmn.pokepediaDamageMultiplier import PokepediaDamageMultiplier
    from pkmn.pokepediaElementType import PokepediaElementType
    from pkmn.pokepediaGeneration import PokepediaGeneration
    from pkmn.pokepediaTypeChart import PokepediaTypeChart


class PokepediaPokemon():

    def __init__(
        self,
        generationElementTypes: Dict[PokepediaGeneration, List[PokepediaElementType]],
        initialGeneration: PokepediaGeneration,
        height: int,
        pokedexId: int,
        weight: int,
        name: str
    ):
        if not utils.hasItems(generationElementTypes):
            raise ValueError(f'generationElementTypes argument is malformed: \"{generationElementTypes}\"')
        elif initialGeneration is None:
            raise ValueError(f'initialGeneration argument is malformed: \"{initialGeneration}\"')
        elif not utils.isValidNum(height):
            raise ValueError(f'height argument is malformed: \"{height}\"')
        elif not utils.isValidNum(pokedexId):
            raise ValueError(f'pokedexId argument is malformed: \"{pokedexId}\"')
        elif not utils.isValidNum(weight):
            raise ValueError(f'weight argument is malformed: \"{weight}\"')
        elif not utils.isValidStr(name):
            raise ValueError(f'name argument is malformed: \"{name}\"')

        self.__generationElementTypes: Dict[PokepediaGeneration, List[PokepediaElementType]] = generationElementTypes
        self.__initialGeneration: PokepediaGeneration = initialGeneration
        self.__height: int = height
        self.__pokedexId: int = pokedexId
        self.__weight: int = weight
        self.__name: str = name

    def __buildGenerationElementTypesWeaknessesAndResistancesStr(
        self,
        weaknessesAndResistances: Dict[PokepediaDamageMultiplier, List[PokepediaElementType]],
        damageMultiplier: PokepediaDamageMultiplier,
        delimiter: str
    ) -> str:
        if not utils.hasItems(weaknessesAndResistances):
            raise ValueError(f'weaknessesAndResistances argument is malformed: \"{weaknessesAndResistances}\"')
        elif damageMultiplier is None:
            raise ValueError(f'damageMultiplier argument is malformed: \"{damageMultiplier}\"')
        elif delimiter is None:
            raise ValueError(f'delimiter argument is malformed: \"{delimiter}\"')

        if damageMultiplier not in weaknessesAndResistances or not utils.hasItems(weaknessesAndResistances[damageMultiplier]):
            return None

        elementTypesStrings: List[str] = list()
        for elementType in weaknessesAndResistances[damageMultiplier]:
            elementTypesStrings.append(elementType.getEmojiOrStr().lower())

        elementTypesString = delimiter.join(elementTypesStrings)
        return f'{damageMultiplier.toStr()} {damageMultiplier.getEffectDescription()} {elementTypesString}.'

    def getGenerationElementTypes(self) -> Dict[PokepediaGeneration, List[PokepediaElementType]]:
        return self.__generationElementTypes

    def getHeight(self) -> int:
        return self.__height

    def getHeightStr(self) -> str:
        return locale.format_string("%d", self.__height, grouping = True)

    def getInitialGeneration(self) -> PokepediaGeneration:
        return self.__initialGeneration

    def getName(self) -> str:
        return self.__name

    def getPokedexId(self) -> int:
        return self.__pokedexId

    def getPokedexIdStr(self) -> str:
        return locale.format_string("%d", self.__pokedexId, grouping = True)

    def getWeight(self) -> int:
        return self.__weight

    def getWeightStr(self) -> str:
        return locale.format_string("%d", self.__weight, grouping = True)

    def toStrList(self, delimiter: str = ', ') -> List[str]:
        if delimiter is None:
            raise ValueError(f'delimiter argument is malformed: \"{delimiter}\"')

        strings: List[str] = list()
        strings.append(f'{self.__name} (#{self.getPokedexIdStr()}) — introduced in {self.__initialGeneration.toStr()}, weight is {self.getWeightStr()} and height is {self.getHeightStr()}.')

        for gen in PokepediaGeneration:
            if gen in self.__generationElementTypes:
                genElementTypes = self.__generationElementTypes[gen]

                genElementTypesStrings: List[str] = list()
                for genElementType in genElementTypes:
                    genElementTypesStrings.append(genElementType.toStr().lower())

                genElementTypesString = delimiter.join(genElementTypesStrings)
                message = f'{gen.toStr()} ({genElementTypesString}):'

                typeChart = PokepediaTypeChart.fromPokepediaGeneration(gen)
                weaknessesAndResistances = typeChart.getWeaknessesAndResistancesFor(genElementTypes)

                for damageMultiplier in PokepediaDamageMultiplier:
                    if damageMultiplier is PokepediaDamageMultiplier.ONE:
                        continue

                    damageMultiplierMessage = self.__buildGenerationElementTypesWeaknessesAndResistancesStr(
                        weaknessesAndResistances = weaknessesAndResistances,
                        damageMultiplier = damageMultiplier,
                        delimiter = delimiter
                    )

                    if utils.isValidStr(damageMultiplierMessage):
                        message = f'{message} {damageMultiplierMessage}'

                strings.append(message)

        return strings

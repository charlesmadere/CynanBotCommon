import random
from typing import Any, Dict, List, Optional, Set

try:
    import CynanBotCommon.utils as utils
    from CynanBotCommon.network.exceptions import GenericNetworkException
    from CynanBotCommon.pkmn.pokepediaBerryFlavor import PokepediaBerryFlavor
    from CynanBotCommon.pkmn.pokepediaContestType import PokepediaContestType
    from CynanBotCommon.pkmn.pokepediaDamageClass import PokepediaDamageClass
    from CynanBotCommon.pkmn.pokepediaElementType import PokepediaElementType
    from CynanBotCommon.pkmn.pokepediaGeneration import PokepediaGeneration
    from CynanBotCommon.pkmn.pokepediaMachineType import PokepediaMachineType
    from CynanBotCommon.pkmn.pokepediaMove import PokepediaMove
    from CynanBotCommon.pkmn.pokepediaNature import PokepediaNature
    from CynanBotCommon.pkmn.pokepediaRepository import PokepediaRepository
    from CynanBotCommon.pkmn.pokepediaStat import PokepediaStat
    from CynanBotCommon.timber.timber import Timber
    from CynanBotCommon.trivia.absTriviaQuestion import AbsTriviaQuestion
    from CynanBotCommon.trivia.absTriviaQuestionRepository import \
        AbsTriviaQuestionRepository
    from CynanBotCommon.trivia.multipleChoiceTriviaQuestion import \
        MultipleChoiceTriviaQuestion
    from CynanBotCommon.trivia.triviaDifficulty import TriviaDifficulty
    from CynanBotCommon.trivia.triviaEmoteGenerator import TriviaEmoteGenerator
    from CynanBotCommon.trivia.triviaExceptions import (
        GenericTriviaNetworkException, MalformedTriviaJsonException,
        UnsupportedTriviaTypeException)
    from CynanBotCommon.trivia.triviaIdGenerator import TriviaIdGenerator
    from CynanBotCommon.trivia.triviaSettingsRepository import \
        TriviaSettingsRepository
    from CynanBotCommon.trivia.triviaSource import TriviaSource
    from CynanBotCommon.trivia.triviaType import TriviaType
    from CynanBotCommon.trivia.trueFalseTriviaQuestion import \
        TrueFalseTriviaQuestion
except:
    import utils
    from network.exceptions import GenericNetworkException
    from timber.timber import Timber
    from trivia.absTriviaQuestion import AbsTriviaQuestion
    from trivia.absTriviaQuestionRepository import AbsTriviaQuestionRepository
    from trivia.multipleChoiceTriviaQuestion import \
        MultipleChoiceTriviaQuestion
    from trivia.triviaDifficulty import TriviaDifficulty
    from trivia.triviaEmoteGenerator import TriviaEmoteGenerator
    from trivia.triviaExceptions import (GenericTriviaNetworkException,
                                         MalformedTriviaJsonException,
                                         UnsupportedTriviaTypeException)
    from trivia.triviaIdGenerator import TriviaIdGenerator
    from trivia.triviaSettingsRepository import TriviaSettingsRepository
    from trivia.triviaSource import TriviaSource
    from trivia.triviaType import TriviaType
    from trivia.trueFalseTriviaQuestion import TrueFalseTriviaQuestion

    from pkmn.pokepediaBerryFlavor import PokepediaBerryFlavor
    from pkmn.pokepediaContestType import PokepediaContestType
    from pkmn.pokepediaDamageClass import PokepediaDamageClass
    from pkmn.pokepediaElementType import PokepediaElementType
    from pkmn.pokepediaGeneration import PokepediaGeneration
    from pkmn.pokepediaMachineType import PokepediaMachineType
    from pkmn.pokepediaMove import PokepediaMove
    from pkmn.pokepediaNature import PokepediaNature
    from pkmn.pokepediaRepository import PokepediaRepository
    from pkmn.pokepediaStat import PokepediaStat


class PkmnTriviaQuestionRepository(AbsTriviaQuestionRepository):

    def __init__(
        self,
        pokepediaRepository: PokepediaRepository,
        timber: Timber,
        triviaEmoteGenerator: TriviaEmoteGenerator,
        triviaIdGenerator: TriviaIdGenerator,
        triviaSettingsRepository: TriviaSettingsRepository,
        maxGeneration: PokepediaGeneration = PokepediaGeneration.GENERATION_3
    ):
        super().__init__(triviaSettingsRepository)

        if not isinstance(pokepediaRepository, PokepediaRepository):
            raise ValueError(f'pokepediaRepository argument is malformed: \"{pokepediaRepository}\"')
        elif not isinstance(timber, Timber):
            raise ValueError(f'timber argument is malformed: \"{timber}\"')
        elif not isinstance(triviaEmoteGenerator, TriviaEmoteGenerator):
            raise ValueError(f'triviaEmoteGenerator argument is malformed: \"{triviaEmoteGenerator}\"')
        elif not isinstance(triviaIdGenerator, TriviaIdGenerator):
            raise ValueError(f'triviaIdGenerator argument is malformed: \"{triviaIdGenerator}\"')
        elif not isinstance(maxGeneration, PokepediaGeneration):
            raise ValueError(f'maxGeneration argument is malformed: \"{maxGeneration}\"')

        self.__pokepediaRepository: PokepediaRepository = pokepediaRepository
        self.__timber: Timber = timber
        self.__triviaEmoteGenerator: TriviaEmoteGenerator = triviaEmoteGenerator
        self.__triviaIdGenerator: TriviaIdGenerator = triviaIdGenerator
        self.__maxGeneration: PokepediaGeneration = maxGeneration

    async def __createMoveContestTypeQuestion(self, move: PokepediaMove) -> Optional[Dict[str, Any]]:
        if not isinstance(move, PokepediaMove):
            raise ValueError(f'move argument is malformed: \"{move}\"')

        if not move.hasContestType():
            return None

        falseContestTypes = await self.__selectRandomFalseContestTypes(move.getContestType())

        falseContestTypeStrs: List[str] = list()
        for falseContestType in falseContestTypes:
            falseContestTypeStrs.append(falseContestType.toStr())

        return {
            'correctAnswer': move.getContestType().toStr(),
            'incorrectAnswers': falseContestTypeStrs,
            'question': f'In Pokémon, what is the contest type of {move.getName()}?',
            'triviaType': TriviaType.MULTIPLE_CHOICE
        }

    async def __createMoveIsAvailableAsMachineQuestion(self, move: PokepediaMove) -> Dict[str, Any]:
        if not isinstance(move, PokepediaMove):
            raise ValueError(f'move argument is malformed: \"{move}\"')

        randomGeneration = await self.__selectRandomGeneration(move.getInitialGeneration())

        machinesStrs: List[str] = list()
        for machineType in PokepediaMachineType:
            machinesStrs.append(machineType.toStr())

        machinesStr = '/'.join(machinesStrs)

        return {
            'correctAnswer': move.hasMachines() and randomGeneration in move.getGenerationMachines(),
            'question': f'In Pokémon {randomGeneration.toLongStr()}, {move.getName()} can be taught via {machinesStr}.',
            'triviaType': TriviaType.TRUE_FALSE
        }

    async def __createMoveIsAvailableAsWhichMachineQuestion(self, move: PokepediaMove) -> Optional[Dict[str, Any]]:
        if not isinstance(move, PokepediaMove):
            raise ValueError(f'move argument is malformed: \"{move}\"')

        if not move.hasMachines():
            return None

        randomGeneration = await self.__selectRandomGeneration(move.getInitialGeneration())
        machine = move.getGenerationMachines()[randomGeneration][0]
        correctMachineNumber = machine.getMachineNumber()
        machinePrefix = machine.getMachineType().toStr()

        falseMachineNumbers = await self.__selectRandomFalseMachineNumbers(
            actualMachineNumber = correctMachineNumber,
            actualMachineType = machine.getMachineType()
        )

        falseMachineNumbersStrs: List[str] = list()
        for falseMachineNumber in falseMachineNumbers:
            falseMachineNumbersStrs.append(f'{machinePrefix}{falseMachineNumber}')

        return {
            'correctAnswer': machine.getMachineName(),
            'incorrectAnswers': falseMachineNumbersStrs,
            'question': f'In Pokémon {randomGeneration.toLongStr()}, {move.getName()} can be taught via which {machinePrefix}?',
            'triviaType': TriviaType.MULTIPLE_CHOICE
        }

    async def __createMoveQuestion(self) -> Dict[str, Any]:
        try:
            move = await self.__pokepediaRepository.fetchRandomMove(
                maxGeneration = self.__maxGeneration
            )
        except GenericNetworkException as e:
            self.__timber.log('PkmnTriviaQuestionRepository', f'Encountered network error when fetching trivia question: {e}', e)
            raise GenericTriviaNetworkException(self.getTriviaSource(), e)

        triviaDict: Optional[Dict[str, Any]] = None

        while triviaDict is None:
            randomTriviaType = random.randint(0, 2)

            if randomTriviaType == 0:
                triviaDict = await self.__createMoveContestTypeQuestion(move)
            elif randomTriviaType == 1:
                triviaDict = await self.__createMoveIsAvailableAsMachineQuestion(move)
            elif randomTriviaType == 2:
                triviaDict = await self.__createMoveIsAvailableAsWhichMachineQuestion(move)
            else:
                raise RuntimeError(f'PkmnTriviaQuestionRepository\'s randomTriviaType value is out of bounds: \"{randomTriviaType}\"!')

        return triviaDict

    async def __createNatureQuestion(self) -> Dict[str, Any]:
        try:
            nature = await self.__pokepediaRepository.fetchRandomNature()
        except GenericNetworkException as e:
            self.__timber.log('PkmnTriviaQuestionRepository', f'Encountered network error when fetching trivia question: {e}', e)
            raise GenericTriviaNetworkException(self.getTriviaSource(), e)

        triviaDict: Optional[Dict[str, Any]] = None

        while triviaDict is None:
            randomTriviaType = random.randint(0, 1)

            if randomTriviaType == 0:
                triviaDict = await self.__createNatureBerryFlavorQuestion(
                    nature = nature,
                    berryFlavor = nature.getLikesFlavor(),
                    likeOrDislikeStr = 'like'
                )
            elif randomTriviaType == 1:
                triviaDict = await self.__createNatureBerryFlavorQuestion(
                    nature = nature,
                    berryFlavor = nature.getHatesFlavor(),
                    likeOrDislikeStr = 'dislike'
                )
            else:
                raise RuntimeError(f'PkmnTriviaQuestionRepository\'s randomTriviaType value is out of bounds: \"{randomTriviaType}\"!')

        return triviaDict

    async def __createNatureBerryFlavorQuestion(
        self,
        nature: PokepediaNature,
        berryFlavor: Optional[PokepediaBerryFlavor],
        likeOrDislikeStr: str
    ) -> Dict[str, Any]:
        if not isinstance(nature, PokepediaNature):
            raise ValueError(f'nature argument is malformed: \"{nature}\"')
        elif berryFlavor is not None and not isinstance(berryFlavor, PokepediaBerryFlavor):
            raise ValueError(f'berryFlavor argument is malformed: \"{berryFlavor}\"')
        elif not utils.isValidStr(likeOrDislikeStr):
            raise ValueError(f'likeOrDislikeStr argument is malformed: \"{likeOrDislikeStr}\"')

        randomFlavors = await self.__selectRandomFalseBerryFlavors(berryFlavor)

        flavorsStrs: List[str] = list()
        for randomFlavor in randomFlavors:
            flavorsStrs.append(randomFlavor.toStr())

        noneOfThese = 'None of these'
        flavorsStrs.append(noneOfThese)

        correctAnswer = ''
        if berryFlavor is None:
            correctAnswer = noneOfThese
        else:
            correctAnswer = berryFlavor.toStr()

        return {
            'correctAnswer': correctAnswer,
            'incorrectAnswers': flavorsStrs,
            'question': f'Pokémon with the nature {nature.toStr()} {likeOrDislikeStr} ONE of the following flavors.',
            'triviaType': TriviaType.MULTIPLE_CHOICE
        }

    async def __createPhysicalOrSpecialQuestion(self) -> Dict[str, Any]:
        applicableDamageClasses: List[PokepediaDamageClass] = [
            PokepediaDamageClass.PHYSICAL, PokepediaDamageClass.SPECIAL
        ]

        actualDamageClass = random.choice(applicableDamageClasses)

        applicableElementTypes: List[PokepediaElementType] = [
            PokepediaElementType.BUG, PokepediaElementType.DARK, PokepediaElementType.DRAGON,
            PokepediaElementType.ELECTRIC, PokepediaElementType.FIGHTING, PokepediaElementType.FIRE,
            PokepediaElementType.FLYING, PokepediaElementType.GHOST, PokepediaElementType.GRASS,
            PokepediaElementType.GROUND, PokepediaElementType.ICE, PokepediaElementType.NORMAL,
            PokepediaElementType.POISON, PokepediaElementType.PSYCHIC, PokepediaElementType.ROCK,
            PokepediaElementType.STEEL, PokepediaElementType.WATER
        ]

        actualElementType = random.choice(applicableElementTypes)

        while actualElementType is None or PokepediaDamageClass.getTypeBasedDamageClass(actualElementType) is not actualDamageClass:
            actualElementType = random.choice(applicableElementTypes)

        minResponses = await self._triviaSettingsRepository.getMinMultipleChoiceResponses()
        maxResponses = await self._triviaSettingsRepository.getMaxMultipleChoiceResponses()
        maxResponses = min(maxResponses, len(PokepediaElementType) - 1)
        responses = random.randint(minResponses, maxResponses)

        falseElementTypes: Set[PokepediaElementType] = set()
        while len(falseElementTypes) < responses:
            falseElementType = random.choice(applicableElementTypes)

            if PokepediaDamageClass.getTypeBasedDamageClass(falseElementType) is not actualDamageClass:
                falseElementTypes.add(falseElementType)

        falseElementTypesStrs: List[str] = list()
        for falseElementType in falseElementTypes:
            falseElementTypesStrs.append(falseElementType.toStr())

        return {
            'correctAnswer': actualElementType.toStr(),
            'incorrectAnswers': falseElementTypesStrs,
            'question': f'In Pokémon generations 1 through 3, which one of the following types has a {actualDamageClass.toStr().lower()} damage class?',
            'triviaType': TriviaType.MULTIPLE_CHOICE
        }

    async def __createPokemonQuestion(self) -> Dict[str, Any]:
        try:
            pokemon = await self.__pokepediaRepository.fetchRandomPokemon(
                maxGeneration = self.__maxGeneration
            )
        except GenericNetworkException as e:
            self.__timber.log('PkmnTriviaQuestionRepository', f'Encountered network error when fetching trivia question: {e}', e)
            raise GenericTriviaNetworkException(self.getTriviaSource(), e)

        randomGeneration = await self.__selectRandomGeneration(pokemon.getInitialGeneration())
        correctTypes = pokemon.getCorrespondingGenerationElementTypes(randomGeneration)
        correctType = random.choice(correctTypes)

        falseTypes = await self.__selectRandomFalseElementTypes(correctTypes)

        falseTypesStrs: List[str] = list()
        for falseType in falseTypes:
            falseTypesStrs.append(falseType.toStr())

        return {
            'correctAnswer': correctType.toStr(),
            'incorrectAnswers': falseTypesStrs,
            'question': f'In Pokémon {randomGeneration.toLongStr()}, {pokemon.getName()} is ONE of the following types?',
            'triviaType': TriviaType.MULTIPLE_CHOICE
        }

    async def __createStatOrNatureQuestion(self) -> Dict[str, Any]:
        randomTriviaType = random.randint(0, 1)

        if randomTriviaType == 0:
            return await self.__createStatQuestion()
        elif randomTriviaType == 1:
            return await self.__createNatureQuestion()
        else:
            raise RuntimeError(f'PkmnTriviaQuestionRepository\'s randomTriviaType value is out of bounds: \"{randomTriviaType}\"!')

    async def __createStatQuestion(self) -> Dict[str, Any]:
        try:
            stat = await self.__pokepediaRepository.fetchRandomStat()
        except GenericNetworkException as e:
            self.__timber.log('PkmnTriviaQuestionRepository', f'Encountered network error when fetching trivia question: {e}', e)
            raise GenericTriviaNetworkException(self.getTriviaSource(), e)

        triviaDict: Optional[Dict[str, Any]] = None

        while triviaDict is None:
            randomTriviaType = random.randint(0, 1)

            if randomTriviaType == 0:
                triviaDict = await self.__createStatDecreasingNaturesQuestion(stat)
            elif randomTriviaType == 1:
                triviaDict = await self.__createStatIncreasingNaturesQuestion(stat)
            else:
                raise RuntimeError(f'PkmnTriviaQuestionRepository\'s randomTriviaType value is out of bounds: \"{randomTriviaType}\"!')

        return triviaDict

    async def __createStatDecreasingNaturesQuestion(self, stat: PokepediaStat) -> Dict[str, Any]:
        if not isinstance(stat, PokepediaStat):
            raise ValueError(f'stat argument is malformed: \"{stat}\"')

        decreasingNatures = stat.getDecreasingNatures()
        randomNature = random.choice(list(PokepediaNature))

        return {
            'correctAnswer': decreasingNatures is not None and randomNature in decreasingNatures,
            'question': f'In Pokémon, the {stat.toStr()} stat is negatively impacted by the {randomNature.toStr()} nature.',
            'triviaType': TriviaType.TRUE_FALSE
        }

    async def __createStatIncreasingNaturesQuestion(self, stat: PokepediaStat) -> Dict[str, Any]:
        if not isinstance(stat, PokepediaStat):
            raise ValueError(f'stat argument is malformed: \"{stat}\"')

        increasingNatures = stat.getIncreasingNatures()
        randomNature = random.choice(list(PokepediaNature))

        return {
            'correctAnswer': increasingNatures is not None and randomNature in increasingNatures,
            'question': f'In Pokémon, the {stat.toStr()} stat is positively impacted by the {randomNature.toStr()} nature.',
            'triviaType': TriviaType.TRUE_FALSE
        }

    async def fetchTriviaQuestion(self, twitchChannel: str) -> AbsTriviaQuestion:
        if not utils.isValidStr(twitchChannel):
            raise ValueError(f'twitchChannel argument is malformed: \"{twitchChannel}\"')

        self.__timber.log('PkmnTriviaQuestionRepository', f'Fetching trivia question... (twitchChannel={twitchChannel})')

        randomTriviaType = random.randint(0, 6)
        triviaDict: Optional[Dict[str, Any]] = None

        if randomTriviaType <= 2:
            triviaDict = await self.__createPokemonQuestion()
        elif randomTriviaType == 4:
            triviaDict = await self.__createMoveQuestion()
        elif randomTriviaType == 5:
            triviaDict = await self.__createStatOrNatureQuestion()
        elif randomTriviaType == 6:
            triviaDict = await self.__createPhysicalOrSpecialQuestion()
        else:
            raise RuntimeError(f'PkmnTriviaQuestionRepository\'s randomTriviaType value is out of bounds: \"{randomTriviaType}\"!')

        if not utils.hasItems(triviaDict):
            raise MalformedTriviaJsonException(f'PkmnTriviaQuestionRepository\'s triviaDict is null/empty: \"{triviaDict}\"!')

        category = 'Pokémon'
        triviaDifficulty = TriviaDifficulty.UNKNOWN
        triviaType: TriviaType = triviaDict['triviaType']
        emote = await self.__triviaEmoteGenerator.getNextEmoteFor(twitchChannel)
        question = utils.getStrFromDict(triviaDict, 'question')

        triviaId = await self.__triviaIdGenerator.generate(
            question = question,
            category = category,
            difficulty = triviaDifficulty.toStr()
        )

        if triviaType is TriviaType.MULTIPLE_CHOICE:
            correctAnswers: List[str] = list()
            correctAnswers.append(utils.getStrFromDict(triviaDict, 'correctAnswer'))
            incorrectAnswers: List[str] = triviaDict['incorrectAnswers']

            multipleChoiceResponses = await self._buildMultipleChoiceResponsesList(
                correctAnswers = correctAnswers,
                multipleChoiceResponses = incorrectAnswers
            )

            return MultipleChoiceTriviaQuestion(
                correctAnswers = correctAnswers,
                multipleChoiceResponses = multipleChoiceResponses,
                category = category,
                categoryId = None,
                emote = emote,
                question = question,
                triviaId = triviaId,
                triviaDifficulty = triviaDifficulty,
                triviaSource = TriviaSource.POKE_API
            )
        elif triviaType is TriviaType.TRUE_FALSE:
            correctAnswers: List[bool] = list()
            correctAnswers.append(utils.getBoolFromDict(triviaDict, 'correctAnswer'))

            return TrueFalseTriviaQuestion(
                correctAnswers = correctAnswers,
                category = category,
                categoryId = None,
                emote = emote,
                question = question,
                triviaId = triviaId,
                triviaDifficulty = triviaDifficulty,
                triviaSource = TriviaSource.POKE_API
            )

        raise UnsupportedTriviaTypeException(f'triviaType \"{triviaType}\" is not supported for Pkmn Trivia: {triviaDict}')

    def getSupportedTriviaTypes(self) -> List[TriviaType]:
        return [ TriviaType.MULTIPLE_CHOICE, TriviaType.TRUE_FALSE ]

    def getTriviaSource(self) -> TriviaSource:
        return TriviaSource.POKE_API

    async def __selectRandomFalseBerryFlavors(
        self,
        actualFlavor: Optional[PokepediaBerryFlavor]
    ) -> Set[PokepediaBerryFlavor]:
        if actualFlavor is not None and not isinstance(actualFlavor, PokepediaBerryFlavor):
            raise ValueError(f'actualFlavor argument is malformed: \"{actualFlavor}\"')

        allFlavors = list(PokepediaBerryFlavor)
        falseFlavors: Set[PokepediaBerryFlavor] = set()

        minResponses = await self._triviaSettingsRepository.getMinMultipleChoiceResponses()
        maxResponses = await self._triviaSettingsRepository.getMaxMultipleChoiceResponses()
        maxResponses = min(maxResponses, len(PokepediaBerryFlavor) - 1)
        responses = random.randint(minResponses, maxResponses)

        while len(falseFlavors) < responses:
            randomFlavor = random.choice(allFlavors)

            if randomFlavor is not actualFlavor:
                falseFlavors.add(randomFlavor)

        return falseFlavors

    async def __selectRandomFalseContestTypes(
        self,
        actualType: PokepediaContestType
    ) -> Set[PokepediaContestType]:
        if not isinstance(actualType, PokepediaContestType):
            raise ValueError(f'actualType argument is malformed: \"{actualType}\"')

        allTypes = list(PokepediaContestType)
        falseTypes: Set[PokepediaContestType] = set()

        minResponses = await self._triviaSettingsRepository.getMinMultipleChoiceResponses()
        maxResponses = await self._triviaSettingsRepository.getMaxMultipleChoiceResponses()
        maxResponses = min(maxResponses, len(PokepediaContestType) - 1)
        responses = random.randint(minResponses, maxResponses)

        while len(falseTypes) < responses:
            randomType = random.choice(allTypes)

            if randomType is not actualType:
                falseTypes.add(randomType)

        return falseTypes

    async def __selectRandomFalseElementTypes(
        self,
        actualTypes: List[PokepediaElementType]
    ) -> Set[PokepediaElementType]:
        if not utils.hasItems(actualTypes):
            raise ValueError(f'actualTypes argument is malformed: \"{actualTypes}\"')

        allTypes = list(PokepediaElementType)
        falseTypes: Set[PokepediaElementType] = set()

        minResponses = await self._triviaSettingsRepository.getMinMultipleChoiceResponses()
        maxResponses = await self._triviaSettingsRepository.getMaxMultipleChoiceResponses()
        maxResponses = min(maxResponses, len(PokepediaElementType) - 1)
        responses = random.randint(minResponses, maxResponses)

        while len(falseTypes) < responses:
            randomType = random.choice(allTypes)

            if randomType not in actualTypes and randomType is not PokepediaElementType.UNKNOWN:
                falseTypes.add(randomType)

        return falseTypes

    async def __selectRandomFalseMachineNumbers(
        self,
        actualMachineNumber: int,
        actualMachineType: PokepediaMachineType
    ) -> Set[int]:
        if not utils.isValidInt(actualMachineNumber):
            raise ValueError(f'actualMachineNumber argument is malformed: \"{actualMachineNumber}\"')
        elif not isinstance(actualMachineType, PokepediaMachineType):
            raise ValueError(f'actualMachineType argument is malformed: \"{actualMachineType}\"')

        falseMachineNumbers: Set[int] = set()

        minResponses = await self._triviaSettingsRepository.getMinMultipleChoiceResponses()
        maxResponses = await self._triviaSettingsRepository.getMaxMultipleChoiceResponses()
        responses = random.randint(minResponses, maxResponses)

        maxMachineNumber: int = None
        if actualMachineType is PokepediaMachineType.HM:
            maxMachineNumber = 12
        elif actualMachineType is PokepediaMachineType.TM:
            maxMachineNumber = 112
        elif actualMachineType is PokepediaMachineType.TR:
            maxMachineNumber = 90
        else:
            raise RuntimeError(f'Can\'t determine `maxMachineNumber` due to unknown PokepediaMachineType: \"{actualMachineType}\"!')

        while len(falseMachineNumbers) < responses:
            randomInt = random.randint(1, maxMachineNumber)

            if randomInt != actualMachineNumber:
                falseMachineNumbers.add(randomInt)

        return falseMachineNumbers

    async def __selectRandomGeneration(
        self,
        initialGeneration: PokepediaGeneration
    ) -> PokepediaGeneration:
        if not isinstance(initialGeneration, PokepediaGeneration):
            raise ValueError(f'initialGeneration argument is malformed: \"{initialGeneration}\"')

        allGenerations = list(PokepediaGeneration)
        indexOfMax = allGenerations.index(self.__maxGeneration)
        indexOfMin = allGenerations.index(initialGeneration)

        if indexOfMax < indexOfMin:
            raise RuntimeError(f'indexOfMax ({indexOfMax}) or indexOfMin ({indexOfMin}) is incompatible with an initial generation of {initialGeneration}! (maxGeneration={self.__maxGeneration}))')

        return allGenerations[random.randint(indexOfMin, indexOfMax)]

import random
from typing import Any, Dict, List, Optional, Set

try:
    import CynanBotCommon.utils as utils
    from CynanBotCommon.network.exceptions import GenericNetworkException
    from CynanBotCommon.pkmn.pokepediaElementType import PokepediaElementType
    from CynanBotCommon.pkmn.pokepediaGeneration import PokepediaGeneration
    from CynanBotCommon.pkmn.pokepediaPokemon import PokepediaPokemon
    from CynanBotCommon.pkmn.pokepediaRepository import PokepediaRepository
    from CynanBotCommon.timber.timber import Timber
    from CynanBotCommon.trivia.absTriviaQuestion import AbsTriviaQuestion
    from CynanBotCommon.trivia.absTriviaQuestionRepository import \
        AbsTriviaQuestionRepository
    from CynanBotCommon.trivia.multipleChoiceTriviaQuestion import \
        MultipleChoiceTriviaQuestion
    from CynanBotCommon.trivia.triviaDifficulty import TriviaDifficulty
    from CynanBotCommon.trivia.triviaEmoteGenerator import TriviaEmoteGenerator
    from CynanBotCommon.trivia.triviaExceptions import (
        GenericTriviaNetworkException, UnsupportedTriviaTypeException)
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
                                         UnsupportedTriviaTypeException)
    from trivia.triviaIdGenerator import TriviaIdGenerator
    from trivia.triviaSettingsRepository import TriviaSettingsRepository
    from trivia.triviaSource import TriviaSource
    from trivia.triviaType import TriviaType
    from trivia.trueFalseTriviaQuestion import TrueFalseTriviaQuestion

    from pkmn.pokepediaElementType import PokepediaElementType
    from pkmn.pokepediaGeneration import PokepediaGeneration
    from pkmn.pokepediaPokemon import PokepediaPokemon
    from pkmn.pokepediaRepository import PokepediaRepository


class PkmnTriviaQuestionRepository(AbsTriviaQuestionRepository):

    def __init__(
        self,
        pokepediaRepository: PokepediaRepository,
        timber: Timber,
        triviaEmoteGenerator: TriviaEmoteGenerator,
        triviaIdGenerator: TriviaIdGenerator,
        triviaSettingsRepository: TriviaSettingsRepository,
        maxGeneration: PokepediaGeneration = PokepediaGeneration.GENERATION_2
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

    async def __createTypeBasedQuestion(
        self,
        generation: PokepediaGeneration,
        pokemon: PokepediaPokemon
    ) -> Dict[str, str]:
        if not isinstance(generation, PokepediaGeneration):
            raise ValueError(f'generation argument is malformed: \"{generation}\"')
        elif not isinstance(pokemon, PokepediaPokemon):
            raise ValueError(f'pokemon argument is malformed: \"{pokemon}\"')

        actualTypes = pokemon.getGenerationElementTypes()[generation]
        falseTypes = await self.__selectRandomFalseTypes(actualTypes)

        finalTypes: List[PokepediaElementType] = list()
        finalTypes.extend(falseTypes)

        correctType = random.choice(actualTypes)
        finalTypes.append(correctType)

        finalTypesStrs: List[str] = list()
        for finalType in finalTypes:
            finalTypesStrs.append(finalType.toStr())

        generationString = await self.__getGenerationString(generation)

        return {
            'correctAnswer': correctType.toStr(),
            'incorrectAnswers': finalTypesStrs,
            'question': f'In Pokémon {generationString}, {pokemon.getName()} is ONE of the following types?'
        }

    async def fetchTriviaQuestion(self, twitchChannel: str) -> AbsTriviaQuestion:
        if not utils.isValidStr(twitchChannel):
            raise ValueError(f'twitchChannel argument is malformed: \"{twitchChannel}\"')

        self.__timber.log('PkmnTriviaQuestionRepository', f'Fetching trivia question... (twitchChannel={twitchChannel})')

        try:
            pokemon = await self.__pokepediaRepository.fetchRandomPokemon(
                maxGeneration = self.__maxGeneration
            )
        except GenericNetworkException as e:
            self.__timber.log('PkmnTriviaQuestionRepository', f'Encountered network error when fetching trivia question: {e}', e)
            raise GenericTriviaNetworkException(self.getTriviaSource(), e)

        category = 'Pokémon'
        triviaDifficulty = TriviaDifficulty.UNKNOWN
        randomGeneration = await self.__selectRandomGeneration(pokemon)

        triviaDict = await self.__createTypeBasedQuestion(
            generation = randomGeneration,
            pokemon = pokemon
        )

        emote = await self.__triviaEmoteGenerator.getNextEmoteFor(twitchChannel)

        question = utils.getStrFromDict(triviaDict, 'question')

        triviaId = await self.__triviaIdGenerator.generate(
            question = question,
            category = category,
            difficulty = triviaDifficulty.toStr()
        )

        triviaType = TriviaType.fromStr(utils.getStrFromDict(triviaDict, 'triviaType'))

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

        raise UnsupportedTriviaTypeException(f'triviaType \"{triviaType}\" is not supported for Pkmn Trivia: {triviaDict}')

    async def __getGenerationString(self, generation: PokepediaGeneration) -> str:
        if not isinstance(generation, PokepediaGeneration):
            raise ValueError(f'generation argument is malformed: \"{generation}\"')

        if generation is PokepediaGeneration.GENERATION_1:
            return 'generation 1'
        elif generation is PokepediaGeneration.GENERATION_2:
            return 'generation 2'
        elif generation is PokepediaGeneration.GENERATION_3:
            return 'generation 3'
        elif generation is PokepediaGeneration.GENERATION_4:
            return 'generation 4'
        elif generation is PokepediaGeneration.GENERATION_5:
            return 'generation 5'
        elif generation is PokepediaGeneration.GENERATION_6:
            return 'generation 6'
        elif generation is PokepediaGeneration.GENERATION_7:
            return 'generation 7'
        elif generation is PokepediaGeneration.GENERATION_8:
            return 'generation 8'
        else:
            raise RuntimeError(f'unknown PokepediaGeneration: \"{generation}\"')

    def getSupportedTriviaTypes(self) -> List[TriviaType]:
        return [ TriviaType.MULTIPLE_CHOICE ]

    def getTriviaSource(self) -> TriviaSource:
        return TriviaSource.POKE_API

    async def __selectRandomFalseTypes(
        self,
        actualTypes: List[PokepediaElementType]
    ) -> Set[PokepediaElementType]:
        if not utils.hasItems(actualTypes):
            raise ValueError(f'actualTypes argument is malformed: \"{actualTypes}\"')

        allTypes = list(PokepediaElementType)
        falseTypes: Set[PokepediaElementType] = set()

        while len(falseTypes) < 4:
            randomType = random.choice(allTypes)

            if randomType not in actualTypes:
                falseTypes.add(randomType)

        return falseTypes

    async def __selectRandomGeneration(self, pokemon: PokepediaPokemon) -> PokepediaGeneration:
        if not isinstance(pokemon, PokepediaPokemon):
            raise ValueError(f'pokemon argument is malformed: \"{pokemon}\"')

        allGenerations = list(PokepediaGeneration)
        indexOfMax: Optional[int] = None
        indexOfMin: Optional[int] = None

        for index, generation in enumerate(allGenerations):
            if generation is self.__maxGeneration:
                indexOfMax = index

            if generation is pokemon.getInitialGeneration():
                indexOfMin = index

            if utils.isValidInt(indexOfMax) and utils.isValidInt(indexOfMin):
                break

        if not utils.isValidInt(indexOfMax) or not utils.isValidInt(indexOfMin) or indexOfMax < indexOfMin:
            raise RuntimeError(f'indexOfMax ({indexOfMax}) or indexOfMin ({indexOfMin}) is incompatible with this Pokemon that has an initial generation of {pokemon.getInitialGeneration()}! (maxGeneration={self.__maxGeneration}))')

        return allGenerations[random.randint(indexOfMin, indexOfMax)]

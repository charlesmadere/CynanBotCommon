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
        BadTriviaSessionTokenException, GenericTriviaNetworkException,
        UnsupportedTriviaTypeException)
    from CynanBotCommon.trivia.triviaIdGenerator import TriviaIdGenerator
    from CynanBotCommon.trivia.triviaQuestionCompiler import \
        TriviaQuestionCompiler
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
    from trivia.triviaExceptions import (BadTriviaSessionTokenException,
                                         GenericTriviaNetworkException,
                                         UnsupportedTriviaTypeException)
    from trivia.triviaIdGenerator import TriviaIdGenerator
    from trivia.triviaQuestionCompiler import TriviaQuestionCompiler
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
    ) -> MultipleChoiceTriviaQuestion:
        if not isinstance(generation, PokepediaGeneration):
            raise ValueError(f'generation argument is malformed: \"{generation}\"')
        elif not isinstance(pokemon, PokepediaPokemon):
            raise ValueError(f'pokemon argument is malformed: \"{pokemon}\"')

        generationString = self.__getGenerationString(generation)

        multipleChoiceQuestions = await self.__createTypesMultipleChoiceSet(
            pokemon = pokemon,
            generation = generation
        )

        question = f'In Pokémon {generationString}, {pokemon.getName()} is ONE of the following types?'

        actualTypes = pokemon.getGenerationElementTypes()[generation]
        falseTypes = self.__selectRandomFalseTypes(actualTypes)
        # TODO
        pass

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
        randomGeneration = self.__selectRandomGeneration()

        return await self.__createTypeBasedQuestion(
            generation = randomGeneration,
            pokemon = pokemon
        )

        raise NotImplementedError()

        triviaId = await self.__triviaIdGenerator.generate(
            category = category,
            difficulty = triviaDifficulty.toStr(),
            question = question
        )

        emote = await self.__triviaEmoteGenerator.getNextEmoteFor(twitchChannel)

        return TrueFalseTriviaQuestion(
            correctAnswers = correctAnswers,
            category = category,
            categoryId = None,
            emote = emote,
            question = question,
            triviaId = triviaId,
            triviaDifficulty = TriviaDifficulty.UNKNOWN,
            triviaSource = triviaSource
        )

    def __getGenerationString(self, generation: PokepediaGeneration) -> str:
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
        return TriviaSource.OPEN_TRIVIA_DATABASE

    def __selectRandomFalseTypes(
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

    def __selectRandomGeneration(self) -> PokepediaGeneration:
        allGenerations = list(PokepediaGeneration)
        indexOfMax = 0

        for index, generation in enumerate(allGenerations):
            if generation is self.__maxGeneration:
                indexOfMax = index
                break

        return allGenerations[random.randint(0, indexOfMax)]

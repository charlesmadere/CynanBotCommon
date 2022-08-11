from asyncio import TimeoutError
from typing import Any, Dict, List

import aiohttp

try:
    import CynanBotCommon.utils as utils
    from CynanBotCommon.networkClientProvider import NetworkClientProvider
    from CynanBotCommon.pkmn.pokepediaDamageClass import PokepediaDamageClass
    from CynanBotCommon.pkmn.pokepediaElementType import PokepediaElementType
    from CynanBotCommon.pkmn.pokepediaGeneration import PokepediaGeneration
    from CynanBotCommon.pkmn.pokepediaMove import PokepediaMove
    from CynanBotCommon.pkmn.pokepediaMoveGeneration import \
        PokepediaMoveGeneration
    from CynanBotCommon.pkmn.pokepediaPokemon import PokepediaPokemon
    from CynanBotCommon.timber.timber import Timber
except:
    import utils
    from networkClientProvider import NetworkClientProvider
    from timber.timber import Timber

    from pkmn.pokepediaDamageClass import PokepediaDamageClass
    from pkmn.pokepediaElementType import PokepediaElementType
    from pkmn.pokepediaGeneration import PokepediaGeneration
    from pkmn.pokepediaMove import PokepediaMove
    from pkmn.pokepediaMoveGeneration import PokepediaMoveGeneration
    from pkmn.pokepediaPokemon import PokepediaPokemon


class PokepediaRepository():

    def __init__(
        self,
        networkClientProvider: NetworkClientProvider,
        timber: Timber
    ):
        if networkClientProvider is None:
            raise ValueError(f'networkClientProvider argument is malformed: \"{networkClientProvider}\"')
        elif timber is None:
            raise ValueError(f'timber argument is malformed: \"{timber}\"')

        self.__networkClientProvider: NetworkClientProvider = networkClientProvider
        self.__timber: Timber = timber

    def __getElementTypeGenerationDictionary(
        self,
        jsonResponse: Dict,
        initialGeneration: PokepediaGeneration
    ) -> Dict[PokepediaGeneration, List[PokepediaElementType]]:
        if jsonResponse is None:
            raise ValueError(f'jsonResponse argument is malformed: \"{jsonResponse}\"')
        elif initialGeneration is None:
            raise ValueError(f'initialGeneration argument is malformed: \"{initialGeneration}\"')

        currentTypesJson = jsonResponse.get('types')
        if not utils.hasItems(currentTypesJson):
            raise ValueError(f'\"types\" field in JSON response is null or empty: {jsonResponse}')

        # begin with current generation types
        currentTypesList: List[PokepediaElementType] = list()
        for currentTypeJson in currentTypesJson:
            currentTypesList.append(PokepediaElementType.fromStr(currentTypeJson['type']['name']))

        pastTypesJson = jsonResponse.get('past_types')
        if pastTypesJson is None:
            raise ValueError(f'\"past_types\" field in JSON response is null: {jsonResponse}')

        elementTypeGenerationDictionary: Dict[PokepediaGeneration, List[PokepediaElementType]] = dict()

        # iterate backwards and insert into dictionary once a generation is found.
        # then 'un-patch' for previous generations.
        for pokepediaGeneration in reversed(PokepediaGeneration):
            for pastTypeJson in pastTypesJson:
                generation = PokepediaGeneration.fromStr(pastTypeJson['generation']['name'])

                if generation is pokepediaGeneration:
                    currentTypesList: List[PokepediaElementType] = list()

                    typesJson = pastTypeJson.get('types')
                    if not utils.hasItems(typesJson):
                        raise ValueError(f'\"types\" field in \"past_types\" JSON array is null or empty: {jsonResponse}')

                    for typeJson in typesJson:
                        currentTypesList.append(PokepediaElementType.fromStr(typeJson['type']['name']))

            elementTypeGenerationDictionary[pokepediaGeneration] = currentTypesList

        # only store typing for generations where this Pokemon actually existed
        for pokepediaGeneration in PokepediaGeneration:
            if pokepediaGeneration.value < initialGeneration.value:
                del elementTypeGenerationDictionary[pokepediaGeneration]

        # remove duplicates
        currentTypesList: List[PokepediaElementType] = None
        for pokepediaGeneration in PokepediaGeneration:
            if pokepediaGeneration in elementTypeGenerationDictionary:
                if currentTypesList is None:
                    currentTypesList = elementTypeGenerationDictionary[pokepediaGeneration]
                elif currentTypesList == elementTypeGenerationDictionary[pokepediaGeneration]:
                    del elementTypeGenerationDictionary[pokepediaGeneration]
                else:
                    currentTypesList = elementTypeGenerationDictionary[pokepediaGeneration]

        return elementTypeGenerationDictionary

    def __getEnDescription(self, jsonResponse: Dict[str, Any]) -> str:
        if not utils.hasItems(jsonResponse):
            raise ValueError(f'jsonResponse argument is malformed: \"{jsonResponse}\"')

        flavorTextEntries = jsonResponse.get('flavor_text_entries')
        if not utils.hasItems(flavorTextEntries):
            raise ValueError(f'\"flavor_text_entries\" field in JSON response is null or empty: {jsonResponse}')

        for flavorTextEntry in flavorTextEntries:
            if flavorTextEntry['language']['name'] == 'en':
                return utils.getStrFromDict(flavorTextEntry, 'flavor_text', clean = True)

        raise RuntimeError(f'can\'t find \"en\" language name in \"flavor_text_entries\" field: {jsonResponse}')

    def __getEnName(self, jsonResponse: Dict[str, Any]) -> str:
        if not utils.hasItems(jsonResponse):
            raise ValueError(f'jsonResponse argument is malformed: \"{jsonResponse}\"')

        names = jsonResponse.get('names')
        if not utils.hasItems(names):
            raise ValueError(f'\"names\" field in JSON response is null or empty: {jsonResponse}')

        for name in names:
            if name['language']['name'] == 'en':
                return utils.getStrFromDict(name, 'name', clean = True).title()

        raise RuntimeError(f'can\'t find \"en\" language name in \"names\" field: {jsonResponse}')

    def __getMoveGenerationDictionary(self, jsonResponse: Dict[str, Any]) -> Dict[PokepediaGeneration, PokepediaMoveGeneration]:
        if not utils.hasItems(jsonResponse):
            raise ValueError(f'jsonResponse argument is malformed: \"{jsonResponse}\"')

        # begin with current generation stats
        accuracy: int = jsonResponse.get('accuracy')
        power: int = jsonResponse.get('power')
        pp = utils.getIntFromDict(jsonResponse, 'pp')
        damageClass = PokepediaDamageClass.fromStr(jsonResponse['damage_class']['name'])
        elementType = PokepediaElementType.fromStr(jsonResponse['type']['name'])
        move: PokepediaMoveGeneration = None

        pastValuesJson = jsonResponse.get('past_values')
        if pastValuesJson is None:
            raise ValueError(f'\"past_values\" field in JSON response is null: {jsonResponse}')

        moveGenerationDictionary: Dict[PokepediaGeneration, PokepediaMoveGeneration] = dict()

        # iterate backwards and insert into dictionary once a generation is found.
        # then 'un-patch' for previous generations.
        for pokepediaGeneration in reversed(PokepediaGeneration):
            for pastValueJson in pastValuesJson:
                generation = PokepediaGeneration.fromStr(pastValueJson['version_group']['name'])

                if generation is pokepediaGeneration:
                    if generation.isEarlyGeneration() and damageClass is not PokepediaDamageClass.STATUS:
                        damageClass = PokepediaDamageClass.getTypeBasedDamageClass(elementType)

                    moveGenerationDictionary[generation] = PokepediaMoveGeneration(
                        accuracy = accuracy,
                        power = power,
                        pp = pp,
                        damageClass = damageClass,
                        elementType = elementType,
                        generation = generation
                    )

                    if utils.isValidNum(pastValueJson.get('accuracy')):
                        accuracy = utils.getIntFromDict(pastValueJson, 'accuracy')

                    if utils.isValidNum(pastValueJson.get('power')):
                        power = utils.getIntFromDict(pastValueJson, 'power')

                    if utils.isValidNum(pastValueJson.get('pp')):
                        pp = utils.getIntFromDict(pastValueJson, 'pp')

                    if pastValueJson.get('type') is not None:
                        elementType = PokepediaElementType.fromStr(pastValueJson['type']['name'])

        generation = PokepediaGeneration.fromStr(jsonResponse['generation']['name'])

        if generation.isEarlyGeneration() and  damageClass is not PokepediaDamageClass.STATUS:
            damageClass = PokepediaDamageClass.getTypeBasedDamageClass(elementType)

        move = PokepediaMoveGeneration(
            accuracy = accuracy,
            power = power,
            pp = pp,
            damageClass = damageClass,
            elementType = elementType,
            generation = generation
        )

        moveGenerationDictionary[generation] = move

        # scan for case where gen4+ type changed but not reflected in past_values JSON array
        if PokepediaGeneration.GENERATION_4 not in moveGenerationDictionary:
            if PokepediaGeneration.GENERATION_3 in moveGenerationDictionary:
                if moveGenerationDictionary[PokepediaGeneration.GENERATION_3].getDamageClass() != damageClass:
                    move = PokepediaMoveGeneration(
                        accuracy = moveGenerationDictionary[PokepediaGeneration.GENERATION_3].getAccuracy(),
                        power = moveGenerationDictionary[PokepediaGeneration.GENERATION_3].getPower(),
                        pp = moveGenerationDictionary[PokepediaGeneration.GENERATION_3].getPp(),
                        damageClass = damageClass,
                        elementType = moveGenerationDictionary[PokepediaGeneration.GENERATION_3].getElementType(),
                        generation = PokepediaGeneration.GENERATION_4
                    )

                    moveGenerationDictionary[PokepediaGeneration.GENERATION_4] = move
            elif PokepediaGeneration.GENERATION_2 in moveGenerationDictionary:
                if moveGenerationDictionary[PokepediaGeneration.GENERATION_2].getDamageClass() != damageClass:
                    move = PokepediaMoveGeneration(
                        accuracy = moveGenerationDictionary[PokepediaGeneration.GENERATION_2].getAccuracy(),
                        power = moveGenerationDictionary[PokepediaGeneration.GENERATION_2].getPower(),
                        pp = moveGenerationDictionary[PokepediaGeneration.GENERATION_2].getPp(),
                        damageClass = damageClass,
                        elementType = moveGenerationDictionary[PokepediaGeneration.GENERATION_2].getElementType(),
                        generation = PokepediaGeneration.GENERATION_4
                    )

                    moveGenerationDictionary[PokepediaGeneration.GENERATION_4] = move
            elif PokepediaGeneration.GENERATION_1 in moveGenerationDictionary:
                if moveGenerationDictionary[PokepediaGeneration.GENERATION_1].getDamageClass() != damageClass:
                    move = PokepediaMoveGeneration(
                        accuracy = moveGenerationDictionary[PokepediaGeneration.GENERATION_1].getAccuracy(),
                        power = moveGenerationDictionary[PokepediaGeneration.GENERATION_1].getPower(),
                        pp = moveGenerationDictionary[PokepediaGeneration.GENERATION_1].getPp(),
                        damageClass = damageClass,
                        elementType = moveGenerationDictionary[PokepediaGeneration.GENERATION_1].getElementType(),
                        generation = PokepediaGeneration.GENERATION_4
                    )

                    moveGenerationDictionary[PokepediaGeneration.GENERATION_4] = move

        # This loop goes through the dictionary of generational moves we've now built up and stored
        # within moveGenerationDictionary and removes any generations that are exact duplicates,
        # UNLESS there exists a generation between the duplicate(s) that is different.
        move = None
        for pokepediaGeneration in PokepediaGeneration:
            if pokepediaGeneration not in moveGenerationDictionary:
                continue
            elif move is None:
                move = moveGenerationDictionary[pokepediaGeneration]
            else:
                comparison = moveGenerationDictionary[pokepediaGeneration]

                if move.getAccuracy() == comparison.getAccuracy() and move.getDamageClass() == comparison.getDamageClass() and move.getElementType() == comparison.getElementType() and move.getPower() == comparison.getPower() and move.getPp() == comparison.getPp():
                    del moveGenerationDictionary[pokepediaGeneration]

                move = comparison

        return moveGenerationDictionary

    async def searchMoves(self, name: str) -> PokepediaMove:
        if not utils.isValidStr(name):
            raise ValueError(f'name argument is malformed: \"{name}\"')

        name = utils.cleanStr(name)
        name = name.replace(' ', '-')
        self.__timber.log('PokepediaRepository', f'Searching PokeAPI for move \"{name}\"...')
        clientSession = await self.__networkClientProvider.get()

        try:
            response = await clientSession.get(f'https://pokeapi.co/api/v2/move/{name}/')
        except (aiohttp.ClientError, TimeoutError) as e:
            self.__timber.log('PokepediaRepository', f'Encountered network error from PokeAPI when searching for \"{name}\" move: {e}')
            raise RuntimeError(f'Encountered network error from PokeAPI when searching for \"{name}\" move: {e}')

        if response.status != 200:
            self.__timber.log('PokepediaRepository', f'Encountered non-200 HTTP status code from PokeAPI when searching for \"{name}\" move: \"{response.status}\"')
            raise RuntimeError(f'Exception occurred due to non-200 HTTP status code from PokeAPI when searching for \"{name}\" move: \"{response.status}\"')

        jsonResponse: Dict[str, Any] = await response.json()
        response.close()

        return PokepediaMove(
            generationMoves = self.__getMoveGenerationDictionary(jsonResponse),
            moveId = utils.getIntFromDict(jsonResponse, 'id'),
            description = self.__getEnDescription(jsonResponse),
            name = self.__getEnName(jsonResponse),
            rawName = utils.getStrFromDict(jsonResponse, 'name')
        )

    async def searchPokemon(self, name: str) -> PokepediaPokemon:
        if not utils.isValidStr(name):
            raise ValueError(f'name argument is malformed: \"{name}\"')

        name = utils.cleanStr(name)
        name = name.replace(' ', '-')
        self.__timber.log('PokepediaRepository', f'Searching PokeAPI for Pokemon \"{name}\"...')
        clientSession = await self.__networkClientProvider.get()

        try:
            response = await clientSession.get(f'https://pokeapi.co/api/v2/pokemon/{name}/')
        except (aiohttp.ClientError, TimeoutError) as e:
            self.__timber.log('PokepediaRepository', f'Encountered network error from PokeAPI when searching for \"{name}\" Pokemon: {e}')
            raise RuntimeError(f'Encountered network error from PokeAPI when searching for \"{name}\" Pokemon: {e}')

        if response.status != 200:
            self.__timber.log('PokepediaRepository', f'Encountered non-200 HTTP status code from PokeAPI when searching for \"{name}\" Pokemon: \"{response.status}\"')
            raise RuntimeError(f'Exception occurred due to non-200 HTTP status code from PokeAPI when searching for \"{name}\" Pokemon: \"{response.status}\"')

        jsonResponse: Dict[str, Any] = await response.json()
        response.close()

        pokedexId = utils.getIntFromDict(jsonResponse, 'id')
        initialGeneration = PokepediaGeneration.fromPokedexId(pokedexId)

        return PokepediaPokemon(
            generationElementTypes = self.__getElementTypeGenerationDictionary(
                jsonResponse = jsonResponse,
                initialGeneration = initialGeneration
            ),
            initialGeneration = initialGeneration,
            height = utils.getIntFromDict(jsonResponse, 'height'),
            pokedexId = pokedexId,
            weight = utils.getIntFromDict(jsonResponse, 'weight'),
            name = utils.getStrFromDict(jsonResponse, 'name').title()
        )

from typing import Dict, List, Optional

import pytest

try:
    from CynanBotCommon.incrementalJsonBuilder import IncrementalJsonBuilder
except:
    from incrementalJsonBuilder import IncrementalJsonBuilder


class TestIncrementalJsonBuilder():

    @pytest.mark.asyncio
    async def test_buildDictionariesOrAppendInternalJsonCache_withEmptyJsonStructure(self):
        builder = IncrementalJsonBuilder()
        result = await builder.buildDictionariesOrAppendInternalJsonCache('{}')
        assert isinstance(result, List)
        assert len(result) == 1
        assert isinstance(result[0], Dict)
        assert len(result[0]) == 0

    @pytest.mark.asyncio
    async def test_buildDictionariesOrAppendInternalJsonCache_withEmptyString(self):
        builder = IncrementalJsonBuilder()
        result = await builder.buildDictionariesOrAppendInternalJsonCache('')
        assert result is None

    @pytest.mark.asyncio
    async def test_buildDictionariesOrAppendInternalJsonCache_withEmptyHalfJsonStructure(self):
        builder = IncrementalJsonBuilder()
        result = await builder.buildDictionariesOrAppendInternalJsonCache('}')
        assert result is None

    @pytest.mark.asyncio
    async def test_buildDictionariesOrAppendInternalJsonCache_withNone(self):
        builder = IncrementalJsonBuilder()
        result = await builder.buildDictionariesOrAppendInternalJsonCache(None)
        assert result is None

    @pytest.mark.asyncio
    async def test_buildDictionariesOrAppendInternalJsonCache_withThreeIncrementalJsonStructures(self):
        builder = IncrementalJsonBuilder()
        result = await builder.buildDictionariesOrAppendInternalJsonCache('{}{\"wor')
        assert isinstance(result, List)
        assert len(result) == 1
        assert isinstance(result[0], Dict)
        assert len(result[0]) == 0

        result = await builder.buildDictionariesOrAppendInternalJsonCache('d\":')
        assert result is None

        result = await builder.buildDictionariesOrAppendInternalJsonCache('\"test\"')
        assert result is None

        result = await builder.buildDictionariesOrAppendInternalJsonCache('}{}{}{\"is_mod":true')
        assert isinstance(result, List)
        assert len(result) == 3
        assert isinstance(result[0], Dict)
        assert len(result[0]) == 1
        assert 'word' in result[0]
        assert isinstance(result[0]['word'], str)
        assert result[0]['word'] == 'test'
        assert isinstance(result[1], Dict)
        assert len(result[1]) == 0
        assert isinstance(result[2], Dict)
        assert len(result[2]) == 0

        result = await builder.buildDictionariesOrAppendInternalJsonCache('}')
        assert isinstance(result, List)
        assert len(result) == 1
        assert isinstance(result[0], Dict)
        assert 'is_mod' in result[0]
        assert isinstance(result[0]['is_mod'], bool)
        assert result[0]['is_mod'] is True

    @pytest.mark.asyncio
    async def test_buildDictionariesOrAppendInternalJsonCache_withTwoEmptyJsonStructures(self):
        builder = IncrementalJsonBuilder()
        result = await builder.buildDictionariesOrAppendInternalJsonCache('{}{}')
        assert isinstance(result, List)
        assert len(result) == 2
        assert isinstance(result[0], Dict)
        assert len(result[0]) == 0
        assert isinstance(result[1], Dict)
        assert len(result[1]) == 0

    @pytest.mark.asyncio
    async def test_buildDictionariesOrAppendInternalJsonCache_withTwoAndAHalfEmptyJsonStructures(self):
        builder = IncrementalJsonBuilder()
        result = await builder.buildDictionariesOrAppendInternalJsonCache('{}{}{')
        assert isinstance(result, List)
        assert len(result) == 2
        assert isinstance(result[0], Dict)
        assert len(result[0]) == 0
        assert isinstance(result[1], Dict)
        assert len(result[1]) == 0

    @pytest.mark.asyncio
    async def test_buildDictionariesOrAppendInternalJsonCache_withWhitespaceString(self):
        builder = IncrementalJsonBuilder()
        result = await builder.buildDictionariesOrAppendInternalJsonCache(' ')
        assert result is None

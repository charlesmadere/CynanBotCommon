import json
from asyncio import TimeoutError
from typing import Any, Dict, Optional

import aiofiles
import aiofiles.ospath
import aiohttp

try:
    import CynanBotCommon.utils as utils
    from CynanBotCommon.funtoon.funtoonPkmnCatchType import \
        FuntoonPkmnCatchType
    from CynanBotCommon.timber.timber import Timber
except:
    import utils
    from timber.timber import Timber

    from funtoon.funtoonPkmnCatchType import FuntoonPkmnCatchType


class FuntoonRepository():

    def __init__(
        self,
        clientSession: aiohttp.ClientSession,
        timber: Timber,
        funtoonApiUrl: str = 'https://funtoon.party/api',
        funtoonRepositoryFile: str = 'CynanBotCommon/funtoon/funtoonRepository.json'
    ):
        if clientSession is None:
            raise ValueError(f'clientSession argument is malformed: \"{clientSession}\"')
        elif timber is None:
            raise ValueError(f'timber argument is malformed: \"{timber}\"')
        elif not utils.isValidUrl(funtoonApiUrl):
            raise ValueError(f'funtoonApiUrl argument is malformed: \"{funtoonApiUrl}\"')
        elif not utils.isValidStr(funtoonRepositoryFile):
            raise ValueError(f'funtoonRepositoryFile argument is malformed: \"{funtoonRepositoryFile}\"')

        self.__clientSession: aiohttp.ClientSession = clientSession
        self.__timber: Timber = timber
        self.__funtoonApiUrl: str = funtoonApiUrl
        self.__funtoonRepositoryFile: str = funtoonRepositoryFile

        self.__cache: Optional[Dict[str, Any]] = None

    async def clearCaches(self):
        self.__cache = None
        self.__timber.log('FuntoonRepository', 'Caches cleared')

    async def getFuntoonToken(self, twitchChannel: str) -> str:
        if not utils.isValidStr(twitchChannel):
            raise ValueError(f'twitchChannel argument is malformed: \"{twitchChannel}\"')

        twitchChannelJson = await self.__readJsonForTwitchChannel(twitchChannel)
        if twitchChannelJson is None:
            return None

        token = twitchChannelJson.get('token')
        if not utils.isValidStr(token):
            raise ValueError(f'\"token\" value for \"{twitchChannel}\" in Funtoon repository file ({self.__funtoonRepositoryFile}) is malformed: \"{token}\"')

        return token

    async def __hitFuntoon(
        self,
        event: str,
        funtoonToken: str,
        twitchChannel: str,
        data: Optional[Any] = None
    ) -> bool:
        if not utils.isValidStr(event):
            raise ValueError(f'event argument is malformed: \"{event}\"')
        elif not utils.isValidStr(funtoonToken):
            raise ValueError(f'funtoonToken argument is malformed: \"{funtoonToken}\"')
        elif not utils.isValidStr(twitchChannel):
            raise ValueError(f'twitchChannel argument is malformed: \"{twitchChannel}\"')

        url = f'{self.__funtoonApiUrl}/events/custom'

        jsonPayload = {
            'channel': twitchChannel,
            'data': data,
            'event': event
        }

        isDebugLoggingEnabled = await self.__isDebugLoggingEnabled()

        if isDebugLoggingEnabled:
            self.__timber.log('FuntoonRepository', f'Hitting Funtoon API \"{url}\" for \"{twitchChannel}\" for event \"{event}\" with JSON payload: {jsonPayload}')

        try:
            response = await self.__clientSession.post(
                url = url,
                headers = {
                    'Authorization': funtoonToken,
                    'Content-Type': 'application/json'
                },
                json = jsonPayload
            )
        except (aiohttp.ClientError, TimeoutError) as e:
            self.__timber.log('FuntoonRepository', f'Encountered network error for \"{twitchChannel}\" for event \"{event}\": {e}')
            return False

        if response is not None and response.status == 200:
            response.close()

            if isDebugLoggingEnabled:
                self.__timber.log('FuntoonRepository', f'Successfully hit Funtoon API \"{url}\" for \"{twitchChannel}\" for event \"{event}\"')

            return True
        else:
            self.__timber.log('FuntoonRepository', f'Error when hitting Funtoon API \"{url}\" for \"{twitchChannel}\" for event \"{event}\" with token \"{funtoonToken}\" with JSON payload: {jsonPayload}, response: \"{response}\"')
            response.close()
            return False

    async def __isDebugLoggingEnabled(self) -> bool:
        jsonContents = await self.__readAllJson()
        return utils.getBoolFromDict(jsonContents, 'debugLoggingEnabled', fallback = False)

    async def pkmnBattle(self, userThatRedeemed: str, userToBattle: str, twitchChannel: str) -> bool:
        if not utils.isValidStr(userThatRedeemed):
            raise ValueError(f'userThatRedeemed argument is malformed: \"{userThatRedeemed}\"')
        elif not utils.isValidStr(userToBattle):
            raise ValueError(f'userToBattle argument is malformed: \"{userToBattle}\"')
        elif not utils.isValidStr(twitchChannel):
            raise ValueError(f'twitchChannel argument is malformed: \"{twitchChannel}\"')

        funtoonToken = await self.getFuntoonToken(twitchChannel)

        if not utils.isValidStr(funtoonToken):
            self.__timber.log('FuntoonRepository', f'Can\'t perform pkmnBattle as twitchChannel \"{twitchChannel}\" has no Funtoon token: \"{funtoonToken}\"')
            return False

        return await self.__hitFuntoon(
            event = 'battle',
            funtoonToken = funtoonToken,
            twitchChannel = twitchChannel,
            data = {
                'player': userThatRedeemed,
                'opponent': userToBattle
            }
        )

    async def pkmnCatch(
        self,
        userThatRedeemed: str,
        twitchChannel: str,
        funtoonPkmnCatchType: FuntoonPkmnCatchType = None
    ) -> bool:
        if not utils.isValidStr(userThatRedeemed):
            raise ValueError(f'userThatRedeemed argument is malformed: \"{userThatRedeemed}\"')
        elif not utils.isValidStr(twitchChannel):
            raise ValueError(f'twitchChannel argument is malformed: \"{twitchChannel}\"')

        funtoonToken = await self.getFuntoonToken(twitchChannel)

        if not utils.isValidStr(funtoonToken):
            self.__timber.log('FuntoonRepository', f'Can\'t perform pkmnCatch as twitchChannel \"{twitchChannel}\" has no Funtoon token: \"{funtoonToken}\"')
            return False

        data = None
        if funtoonPkmnCatchType is None:
            data = userThatRedeemed
        else:
            data = {
                'who': userThatRedeemed,
                'catchType': funtoonPkmnCatchType.toStr()
            }

        return await self.__hitFuntoon(
            event = 'catch',
            funtoonToken = funtoonToken,
            twitchChannel = twitchChannel,
            data = data
        )

    async def pkmnGiveEvolve(self, userThatRedeemed: str, twitchChannel: str) -> bool:
        if not utils.isValidStr(userThatRedeemed):
            raise ValueError(f'userThatRedeemed argument is malformed: \"{userThatRedeemed}\"')
        elif not utils.isValidStr(twitchChannel):
            raise ValueError(f'twitchChannel argument is malformed: \"{twitchChannel}\"')

        funtoonToken = await self.getFuntoonToken(twitchChannel)

        if not utils.isValidStr(funtoonToken):
            self.__timber.log('FuntoonRepository', f'Can\'t perform pkmnGiveEvolve as twitchChannel \"{twitchChannel}\" has no Funtoon token: \"{funtoonToken}\"')
            return False

        return await self.__hitFuntoon(
            event = 'giveFreeEvolve',
            funtoonToken = funtoonToken,
            twitchChannel = twitchChannel,
            data = userThatRedeemed
        )

    async def pkmnGiveShiny(self, userThatRedeemed: str, twitchChannel: str) -> bool:
        if not utils.isValidStr(userThatRedeemed):
            raise ValueError(f'userThatRedeemed argument is malformed: \"{userThatRedeemed}\"')
        elif not utils.isValidStr(twitchChannel):
            raise ValueError(f'twitchChannel argument is malformed: \"{twitchChannel}\"')

        funtoonToken = await self.getFuntoonToken(twitchChannel)

        if not utils.isValidStr(funtoonToken):
            self.__timber.log('FuntoonRepository', f'Can\'t perform pkmnGiveShiny as twitchChannel \"{twitchChannel}\" has no Funtoon token: \"{funtoonToken}\"')
            return False

        return await self.__hitFuntoon(
            event = 'giveFreeShiny',
            funtoonToken = funtoonToken,
            twitchChannel = twitchChannel,
            data = userThatRedeemed
        )

    async def __readAllJson(self) -> Dict[str, Any]:
        if self.__cache:
            return self.__cache

        if not await aiofiles.ospath.exists(self.__funtoonRepositoryFile):
            raise FileNotFoundError(f'Funtoon repository file not found: \"{self.__funtoonRepositoryFile}\"')

        async with aiofiles.open(self.__funtoonRepositoryFile, mode = 'r') as file:
            data = await file.read()
            jsonContents = json.loads(data)

        if jsonContents is None:
            raise IOError(f'Error reading from Funtoon repository file: \"{self.__funtoonRepositoryFile}\"')
        elif len(jsonContents) == 0:
            raise ValueError(f'JSON contents of Funtoon repository file \"{self.__funtoonRepositoryFile}\" is empty')

        self.__cache = jsonContents
        return jsonContents

    async def __readJsonForTwitchChannel(self, twitchChannel: str) -> Dict[str, Any]:
        if not utils.isValidStr(twitchChannel):
            raise ValueError(f'twitchChannel argument is malformed: \"{twitchChannel}\"')

        jsonContents = await self.__readAllJson()
        twitchChannelsJson: Dict[str, Any] = jsonContents.get('twitchChannels')
        if not utils.hasItems(twitchChannelsJson):
            raise ValueError(f'\"twitchChannels\" JSON contents of Funtoon repository file \"{self.__funtoonRepositoryFile}\" is missing/empty')

        twitchChannel = twitchChannel.lower()

        for key in twitchChannelsJson:
            if key.lower() == twitchChannel:
                return twitchChannelsJson[key]

        return None

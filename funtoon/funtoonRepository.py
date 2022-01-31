import json
import os
from typing import Dict

import requests
from requests import ConnectionError, HTTPError, Timeout
from requests.exceptions import ReadTimeout, TooManyRedirects
from urllib3.exceptions import MaxRetryError, NewConnectionError

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
        timber: Timber,
        funtoonApiUrl: str = 'https://funtoon.party/api',
        funtoonRepositoryFile: str = 'CynanBotCommon/funtoon/funtoonRepository.json'
    ):
        if timber is None:
            raise ValueError(f'timber argument is malformed: \"{timber}\"')
        elif not utils.isValidUrl(funtoonApiUrl):
            raise ValueError(f'funtoonApiUrl argument is malformed: \"{funtoonApiUrl}\"')
        elif not utils.isValidStr(funtoonRepositoryFile):
            raise ValueError(f'funtoonRepositoryFile argument is malformed: \"{funtoonRepositoryFile}\"')

        self.__timber: Timber = timber
        self.__funtoonApiUrl: str = funtoonApiUrl
        self.__funtoonRepositoryFile: str = funtoonRepositoryFile

    def getFuntoonToken(self, twitchChannel: str) -> str:
        if not utils.isValidStr(twitchChannel):
            raise ValueError(f'twitchChannel argument is malformed: \"{twitchChannel}\"')

        twitchChannelJson = self.__readJsonForTwitchChannel(twitchChannel)
        if twitchChannelJson is None:
            return None

        token = twitchChannelJson.get('token')
        if not utils.isValidStr(token):
            raise ValueError(f'\"token\" value for \"{twitchChannel}\" in Funtoon repository file ({self.__funtoonRepositoryFile}) is malformed: \"{token}\"')

        return token

    def __hitFuntoon(
        self,
        event: str,
        funtoonToken: str,
        twitchChannel: str,
        data = None
    ) -> bool:
        if not utils.isValidStr(event):
            raise ValueError(f'event argument is malformed: \"{event}\"')
        elif not utils.isValidStr(funtoonToken):
            raise ValueError(f'funtoonToken argument is malformed: \"{funtoonToken}\"')
        elif not utils.isValidStr(twitchChannel):
            raise ValueError(f'twitchChannel argument is malformed: \"{twitchChannel}\"')

        url: str = f'{self.__funtoonApiUrl}/events/custom'

        jsonPayload: Dict = {
            'channel': twitchChannel,
            'data': data,
            'event': event
        }

        if self.__isDebugLoggingEnabled():
            self.__timber.log('FuntoonRepository', f'Hitting Funtoon API \"{url}\" for \"{twitchChannel}\" for event \"{event}\" with JSON payload:\n{jsonPayload}')

        rawResponse = None
        try:
            rawResponse = requests.post(
                url = url,
                headers = {
                    'Authorization': funtoonToken,
                    'Content-Type': 'application/json'
                },
                json = jsonPayload,
                timeout = utils.getDefaultTimeout()
            )
        except (ConnectionError, HTTPError, MaxRetryError, NewConnectionError, ReadTimeout, Timeout, TooManyRedirects) as e:
            self.__timber.log('FuntoonRepository', f'Exception occurred when attempting to hit Funtoon API \"{url}\" for \"{twitchChannel}\" for event \"{event}\" with JSON payload: {jsonPayload}, and exception: {e}')

        if rawResponse is not None and rawResponse.status_code == 200:
            if self.__isDebugLoggingEnabled():
                self.__timber.log('FuntoonRepository', f'Successfully hit Funtoon API \"{url}\" for \"{twitchChannel}\" for event \"{event}\"')

            return True
        else:
            self.__timber.log('FuntoonRepository', f'Error when hitting Funtoon API \"{url}\" for \"{twitchChannel}\" for evebt \"{event}\" with token \"{funtoonToken}\" with JSON payload: {jsonPayload}, rawResponse: \"{rawResponse}\"')
            return False

    def __isDebugLoggingEnabled(self) -> bool:
        jsonContents = self.__readJson()
        return utils.getBoolFromDict(jsonContents, 'debugLoggingEnabled', False)

    def pkmnBattle(self, userThatRedeemed: str, userToBattle: str, twitchChannel: str) -> bool:
        if not utils.isValidStr(userThatRedeemed):
            raise ValueError(f'userThatRedeemed argument is malformed: \"{userThatRedeemed}\"')
        elif not utils.isValidStr(userToBattle):
            raise ValueError(f'userToBattle argument is malformed: \"{userToBattle}\"')
        elif not utils.isValidStr(twitchChannel):
            raise ValueError(f'twitchChannel argument is malformed: \"{twitchChannel}\"')

        funtoonToken = self.getFuntoonToken(twitchChannel)

        if not utils.isValidStr(funtoonToken):
            return False

        return self.__hitFuntoon(
            event = 'battle',
            funtoonToken = funtoonToken,
            twitchChannel = twitchChannel,
            data = {
                'player': userThatRedeemed,
                'opponent': userToBattle
            }
        )

    def pkmnCatch(
        self,
        userThatRedeemed: str,
        twitchChannel: str,
        funtoonPkmnCatchType: FuntoonPkmnCatchType = None
    ) -> bool:
        if not utils.isValidStr(userThatRedeemed):
            raise ValueError(f'userThatRedeemed argument is malformed: \"{userThatRedeemed}\"')
        elif not utils.isValidStr(twitchChannel):
            raise ValueError(f'twitchChannel argument is malformed: \"{twitchChannel}\"')

        funtoonToken = self.getFuntoonToken(twitchChannel)

        if not utils.isValidStr(funtoonToken):
            return False

        data = None
        if funtoonPkmnCatchType is None:
            data = userThatRedeemed
        else:
            data = {
                'who': userThatRedeemed,
                'catchType': funtoonPkmnCatchType.toStr()
            }

        return self.__hitFuntoon(
            event = 'catch',
            funtoonToken = funtoonToken,
            twitchChannel = twitchChannel,
            data = data
        )

    def pkmnGiveEvolve(self, userThatRedeemed: str, twitchChannel: str) -> bool:
        if not utils.isValidStr(userThatRedeemed):
            raise ValueError(f'userThatRedeemed argument is malformed: \"{userThatRedeemed}\"')
        elif not utils.isValidStr(twitchChannel):
            raise ValueError(f'twitchChannel argument is malformed: \"{twitchChannel}\"')

        funtoonToken = self.getFuntoonToken(twitchChannel)

        if not utils.isValidStr(funtoonToken):
            return False

        return self.__hitFuntoon(
            event = 'giveFreeEvolve',
            funtoonToken = funtoonToken,
            twitchChannel = twitchChannel,
            data = userThatRedeemed
        )

    def pkmnGiveShiny(self, userThatRedeemed: str, twitchChannel: str) -> bool:
        if not utils.isValidStr(userThatRedeemed):
            raise ValueError(f'userThatRedeemed argument is malformed: \"{userThatRedeemed}\"')
        elif not utils.isValidStr(twitchChannel):
            raise ValueError(f'twitchChannel argument is malformed: \"{twitchChannel}\"')

        funtoonToken = self.getFuntoonToken(twitchChannel)

        if not utils.isValidStr(funtoonToken):
            return False

        return self.__hitFuntoon(
            event = 'giveFreeShiny',
            funtoonToken = funtoonToken,
            twitchChannel = twitchChannel,
            data = userThatRedeemed
        )

    def __readJson(self) -> Dict[str, object]:
        if not os.path.exists(self.__funtoonRepositoryFile):
            raise FileNotFoundError(f'Funtoon repository file not found: \"{self.__funtoonRepositoryFile}\"')

        with open(self.__funtoonRepositoryFile, 'r') as file:
            jsonContents = json.load(file)

        if jsonContents is None:
            raise IOError(f'Error reading from Funtoon repository file: \"{self.__funtoonRepositoryFile}\"')
        elif len(jsonContents) == 0:
            raise ValueError(f'JSON contents of Funtoon repository file \"{self.__funtoonRepositoryFile}\" is empty')

        return jsonContents

    def __readJsonForTwitchChannel(self, twitchChannel: str) -> Dict[str, object]:
        if not utils.isValidStr(twitchChannel):
            raise ValueError(f'twitchChannel argument is malformed: \"{twitchChannel}\"')

        jsonContents = self.__readJson()

        twitchChannelsJson: Dict[str, object] = jsonContents.get('twitchChannels')
        if not utils.hasItems(twitchChannelsJson):
            raise ValueError(f'\"twitchChannels\" JSON contents of Funtoon repository file \"{self.__funtoonRepositoryFile}\" is missing/empty')

        for key in twitchChannelsJson:
            if key.lower() == twitchChannel.lower():
                return twitchChannelsJson[key]

        return None

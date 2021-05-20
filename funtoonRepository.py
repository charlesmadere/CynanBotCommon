import json
import os
from typing import Dict

import requests
from requests import ConnectionError, HTTPError, Timeout
from urllib3.exceptions import MaxRetryError, NewConnectionError

try:
    import CynanBotCommon.utils as utils
except:
    import utils


class FuntoonRepository():

    def __init__(
        self,
        funtoonApiUrl: str = 'https://funtoon.party/api',
        funtoonRepositoryFile: str = 'CynanBotCommon/funtoonRepository.json'
    ):
        if not utils.isValidUrl(funtoonApiUrl):
            raise ValueError(f'funtoonApiUrl argument is malformed: \"{funtoonApiUrl}\"')
        elif not utils.isValidStr(funtoonRepositoryFile):
            raise ValueError(f'funtoonRepositoryFile argument is malformed: \"{funtoonRepositoryFile}\"')

        self.__funtoonApiUrl = funtoonApiUrl
        self.__funtoonRepositoryFile = funtoonRepositoryFile

    def getFuntoonToken(self, twitchChannel: str) -> str:
        if not utils.isValidStr(twitchChannel):
            raise ValueError(f'twitchChannel argument is malformed: \"{twitchChannel}\"')

        twitchChannelJson = self.__readJson(twitchChannel)
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

        rawResponse = None
        try:
            rawResponse = requests.post(
                url = f'{self.__funtoonApiUrl}/events/custom',
                headers = {
                    'Authorization': funtoonToken,
                    'Content-Type': 'application/json'
                },
                json = {
                    'channel': twitchChannel,
                    'data': data,
                    'event': event
                },
                timeout = utils.getDefaultTimeout()
            )
        except (ConnectionError, HTTPError, MaxRetryError, NewConnectionError, Timeout) as e:
            print(f'Exception occurred when attempting to post Funtoon \"{event}\" event for \"{twitchChannel}\": {e}')

        if rawResponse is not None and rawResponse.status_code == 200:
            return True
        else:
            print(f'Received error when hitting Funtoon API \"{rawResponse.url}\" for \"{twitchChannel}\" for \"{event}\" event with token \"{funtoonToken}\"\nrawResponse: \"{rawResponse}\"')
            return False

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

    def pkmnCatch(self, userThatRedeemed: str, twitchChannel: str) -> bool:
        if not utils.isValidStr(userThatRedeemed):
            raise ValueError(f'userThatRedeemed argument is malformed: \"{userThatRedeemed}\"')
        elif not utils.isValidStr(twitchChannel):
            raise ValueError(f'twitchChannel argument is malformed: \"{twitchChannel}\"')

        funtoonToken = self.getFuntoonToken(twitchChannel)

        if not utils.isValidStr(funtoonToken):
            return False

        return self.__hitFuntoon(
            event = 'catch',
            funtoonToken = funtoonToken,
            twitchChannel = twitchChannel,
            data = userThatRedeemed
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

    def __readJson(self, twitchChannel: str) -> Dict:
        if not utils.isValidStr(twitchChannel):
            raise ValueError(f'twitchChannel argument is malformed: \"{twitchChannel}\"')

        if not os.path.exists(self.__funtoonRepositoryFile):
            raise FileNotFoundError(f'Funtoon repository file not found: \"{self.__funtoonRepositoryFile}\"')

        with open(self.__funtoonRepositoryFile, 'r') as file:
            jsonContents = json.load(file)

        if jsonContents is None:
            raise IOError(f'Error reading from Funtoon repository file: \"{self.__funtoonRepositoryFile}\"')
        elif len(jsonContents) == 0:
            raise ValueError(f'JSON contents of Funtoon repository file \"{self.__funtoonRepositoryFile}\" is empty')

        for key in jsonContents:
            if key.lower() == twitchChannel.lower():
                return jsonContents[key]

        return None

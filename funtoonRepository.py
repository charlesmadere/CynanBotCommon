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

        token = twitchChannelJson['token']
        if not utils.isValidStr(token):
            raise ValueError(f'\"token\" value for \"{twitchChannel}\" in Funtoon repository file ({self.__funtoonRepositoryFile}) is malformed: \"{token}\"')

        return token

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
                    'data': {
                        'player': userThatRedeemed,
                        'opponent': userToBattle
                    },
                    'event': 'battle'
                },
                timeout = utils.getDefaultTimeout()
            )
        except (ConnectionError, HTTPError, MaxRetryError, NewConnectionError, Timeout) as e:
            print(f'Exception occurred when attempting to post Funtoon battle event for \"{twitchChannel}\": {e}')
            raise RuntimeError(f'Exception occurred when attempting to post Funtoon battle event for \"{twitchChannel}\": {e}')

        if rawResponse is not None and rawResponse.status_code == 200:
            return True
        else:
            print(f'Received error when hitting Funtoon pokemon battle API for \"{twitchChannel}\" with token \"{funtoonToken}\"\nrawResponse: \"{rawResponse}\"')
            return False

    def pkmnCatch(self, userThatRedeemed: str, twitchChannel: str):
        if not utils.isValidStr(userThatRedeemed):
            raise ValueError(f'userThatRedeemed argument is malformed: \"{userThatRedeemed}\"')
        elif not utils.isValidStr(twitchChannel):
            raise ValueError(f'twitchChannel argument is malformed: \"{twitchChannel}\"')

        funtoonToken = self.getFuntoonToken(twitchChannel)

        if not utils.isValidStr(funtoonToken):
            return False

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
                    'data': userThatRedeemed,
                    'event': 'catch'
                },
                timeout = utils.getDefaultTimeout()
            )
        except (ConnectionError, HTTPError, MaxRetryError, NewConnectionError, Timeout) as e:
            print(f'Exception occurred when attempting to post Funtoon catch event for \"{twitchChannel}\": {e}')
            raise RuntimeError(f'Exception occurred when attempting to post Funtoon catch event for \"{twitchChannel}\": {e}')

        if rawResponse is not None and rawResponse.status_code == 200:
            return True
        else:
            print(f'Received error when hitting Funtoon pokemon catch API for \"{twitchChannel}\" with token \"{funtoonToken}\"\nrawResponse: \"{rawResponse}\"')
            return False

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

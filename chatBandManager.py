import json
from datetime import timedelta
from enum import Enum, auto
from os import path
from typing import Dict

try:
    import CynanBotCommon.utils as utils
    from CynanBotCommon.timedDict import TimedDict
    from CynanBotCommon.websocketConnectionServer import \
        WebsocketConnectionServer
except:
    import utils
    from timedDict import TimedDict
    from websocketConnectionServer import WebsocketConnectionServer


class ChatBandInstrument(Enum):

    BASS = auto()
    DRUMS = auto()
    GUITAR = auto()
    SYNTH = auto()
    WHISTLE = auto()

    @classmethod
    def fromStr(cls, text: str):
        if not utils.isValidStr(text):
            raise ValueError(f'text argument is malformed: \"{text}\"')

        text = text.lower()

        if text == 'bass':
            return ChatBandInstrument.BASS
        elif text == 'drums':
            return ChatBandInstrument.DRUMS
        elif text == 'guitar':
            return ChatBandInstrument.GUITAR
        elif text == 'synth':
            return ChatBandInstrument.SYNTH
        elif text == 'whistle':
            return ChatBandInstrument.WHISTLE
        else:
            raise ValueError(f'unknown ChatBandInstrument: \"{text}\"')

    def toStr(self) -> str:
        if self is ChatBandInstrument.BASS:
            return 'bass'
        elif self is ChatBandInstrument.DRUMS:
            return 'drums'
        elif self is ChatBandInstrument.GUITAR:
            return 'guitar'
        elif self is ChatBandInstrument.SYNTH:
            return 'synth'
        elif self is ChatBandInstrument.WHISTLE:
            return 'whistle'
        else:
            raise ValueError(f'unknown ChatBandInstrument: \"{self}\"')


class ChatBandMember():

    def __init__(
        self,
        instrument: ChatBandInstrument,
        author: str,
        keyPhrase: str
    ):
        if instrument is None:
            raise ValueError(f'instrument argument is malformed: \"{instrument}\"')
        elif not utils.isValidStr(author):
            raise ValueError(f'author argument is malformed: \"{author}\"')
        elif not utils.isValidStr(keyPhrase):
            raise ValueError(f'keyPhrase argument is malformed: \"{keyPhrase}\"')

        self.__instrument: ChatBandInstrument = instrument
        self.__author: str = author
        self.__keyPhrase: str = keyPhrase

    def getAuthor(self) -> str:
        return self.__author

    def getInstrument(self) -> ChatBandInstrument:
        return self.__instrument

    def getKeyPhrase(self) -> str:
        return self.__keyPhrase

    def toEvent(self) -> str:
        return self.__instrument.toStr()


class ChatBandManager():

    def __init__(
        self,
        websocketConnectionServer: WebsocketConnectionServer,
        chatBandFile: str = 'CynanBotCommon/chatBandManager.json',
        cooldownDelay: timedelta = timedelta(minutes = 5)
    ):
        if websocketConnectionServer is None:
            raise ValueError(f'websocketConnectionServer argument is malformed: \"{websocketConnectionServer}\"')
        elif not utils.isValidStr(chatBandFile):
            raise ValueError(f'chatBandFile argument is malformed: \"{chatBandFile}\"')
        elif cooldownDelay is None:
            raise ValueError(f'cooldownDelay argument is malformed: \"{cooldownDelay}\"')

        self.__websocketConnectionServer: WebsocketConnectionServer = websocketConnectionServer
        self.__chatBandFile: str = chatBandFile
        self.__lastChatBandMessageTimes: TimedDict = TimedDict(cooldownDelay)

    async def playInstrumentForMessage(self, twitchChannel: str, author: str, message: str) -> bool:
        if not utils.isValidStr(twitchChannel):
            raise ValueError(f'twitchChannel argument is malformed: \"{twitchChannel}\"')
        elif not utils.isValidStr(author):
            raise ValueError(f'author argument is malformed: \"{author}\"')
        elif not utils.isValidStr(message):
            raise ValueError(f'message argument is malformed: \"{message}\"')

        if not self.__lastChatBandMessageTimes.isReadyAndUpdate(f'{twitchChannel.lower()}:{author.lower()}'):
            return False

        chatBandMember = self.__readJson(twitchChannel, author)
        if chatBandMember is None or message != chatBandMember.getKeyPhrase():
            return False

        await self.__websocketConnectionServer.sendEvent(chatBandMember.toEvent())
        return True

    def __readAllJson(self) -> Dict:
        if not path.exists(self.__chatBandFile):
            raise FileNotFoundError(f'Chat Band file not found: \"{self.__chatBandFile}\"')

        with open(self.__chatBandFile, 'r') as file:
            jsonContents = json.load(file)

        if jsonContents is None:
            raise IOError(f'Error reading from Chat Band file: \"{self.__chatBandFile}\"')
        elif len(jsonContents) == 0:
            raise ValueError(f'JSON contents of Chat Band file \"{self.__chatBandFile}\" is empty')

        return jsonContents

    def __readJson(self, twitchChannel: str, author: str) -> ChatBandMember:
        if not utils.isValidStr(twitchChannel):
            raise ValueError(f'twitchChannel argument is malformed: \"{twitchChannel}\"')
        elif not utils.isValidStr(author):
            raise ValueError(f'author argument is malformed: \"{author}\"')

        twitchChannelsJson = self.__readAllJson()

        for key in twitchChannelsJson:
            if key.lower() == twitchChannel.lower():
                twitchChannelJson = twitchChannelsJson[key]

                for subKey in twitchChannelJson:
                    if subKey.lower() == author:
                        chatBandMemberJson = twitchChannelJson[subKey]

                        return ChatBandMember(
                            instrument = ChatBandInstrument.fromStr(utils.getStrFromDict(chatBandMemberJson, 'instrument')),
                            author = subKey,
                            keyPhrase = utils.getStrFromDict(chatBandMemberJson, 'keyPhrase')
                        )

                return None

        return None

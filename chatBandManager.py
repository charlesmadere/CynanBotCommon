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

    def toEventData(self) -> Dict:
        return {
            'author': self.__author,
            'keyPhrase': self.__keyPhrase,
            'instrument': self.__instrument.toStr()
        }


class ChatBandManager():

    def __init__(
        self,
        websocketConnectionServer: WebsocketConnectionServer,
        chatBandFile: str = 'CynanBotCommon/chatBandManager.json',
        eventType: str = 'chatBand',
        cooldown: timedelta = timedelta(minutes = 5)
    ):
        if websocketConnectionServer is None:
            raise ValueError(f'websocketConnectionServer argument is malformed: \"{websocketConnectionServer}\"')
        elif not utils.isValidStr(chatBandFile):
            raise ValueError(f'chatBandFile argument is malformed: \"{chatBandFile}\"')
        elif not utils.isValidStr(eventType):
            raise ValueError(f'eventType argument is malformed: \"{eventType}\"')
        elif cooldown is None:
            raise ValueError(f'cooldown argument is malformed: \"{cooldown}\"')

        self.__websocketConnectionServer: WebsocketConnectionServer = websocketConnectionServer
        self.__chatBandFile: str = chatBandFile
        self.__eventType: str = eventType
        self.__lastChatBandMessageTimes: TimedDict = TimedDict(cooldown)
        self.__chatBandMemberCache: TimedDict = TimedDict(cooldown)
        self.__stubChatBandMember: ChatBandMember = ChatBandMember(ChatBandInstrument.BASS, "author", "keyPhrase")

    async def playInstrumentForMessage(self, twitchChannel: str, author: str, message: str) -> bool:
        if not utils.isValidStr(twitchChannel):
            raise ValueError(f'twitchChannel argument is malformed: \"{twitchChannel}\"')
        elif not utils.isValidStr(author):
            raise ValueError(f'author argument is malformed: \"{author}\"')
        elif not utils.isValidStr(message):
            raise ValueError(f'message argument is malformed: \"{message}\"')

        chatBandMember = self.__findChatBandMember(
            twitchChannel = twitchChannel,
            author = author,
            message = message
        )

        if chatBandMember is None:
            return False
        elif chatBandMember is self.__stubChatBandMember:
            return False
        elif not self.__lastChatBandMessageTimes.isReadyAndUpdate(self.__getCooldownKey(twitchChannel, author)):
            return False

        await self.__websocketConnectionServer.sendEvent(
            twitchChannel = twitchChannel,
            eventType = self.__eventType,
            eventData = chatBandMember.toEventData()
        )

        return True

    def __findChatBandMember(
        self,
        twitchChannel: str,
        author: str,
        message: str
    ) -> ChatBandMember:
        if not utils.isValidStr(twitchChannel):
            raise ValueError(f'twitchChannel argument is malformed: \"{twitchChannel}\"')
        elif not utils.isValidStr(author):
            raise ValueError(f'author argument is malformed: \"{author}\"')
        elif not utils.isValidStr(message):
            raise ValueError(f'message argument is malformed: \"{message}\"')

        chatBandMember: ChatBandMember = self.__chatBandMemberCache[self.__getCooldownKey(twitchChannel, author)]

        if chatBandMember is None:
            jsonContents = self.__readJson(twitchChannel)

            if utils.hasItems(jsonContents):
                for key in jsonContents:
                    if key.lower() == author.lower():
                        chatBandMemberJson = jsonContents[key]

                        chatBandMember = ChatBandMember(
                            instrument = ChatBandInstrument.fromStr(utils.getStrFromDict(chatBandMemberJson, 'instrument')),
                            author = key,
                            keyPhrase = utils.getStrFromDict(chatBandMemberJson, 'keyPhrase')
                        )

                        self.__chatBandMemberCache[self.__getCooldownKey(twitchChannel, author)] = chatBandMember
                        break

        if chatBandMember is None:
            self.__chatBandMemberCache[self.__getCooldownKey(twitchChannel, author)] = self.__stubChatBandMember

        if chatBandMember is not None and chatBandMember is not self.__stubChatBandMember and chatBandMember.getKeyPhrase() == message:
            return chatBandMember
        else:
            return None

    def __getCooldownKey(self, twitchChannel: str, author: str) -> str:
        if not utils.isValidStr(twitchChannel):
            raise ValueError(f'twitchChannel argument is malformed: \"{twitchChannel}\"')
        elif not utils.isValidStr(author):
            raise ValueError(f'author argument is malformed: \"{author}\"')

        return f'{twitchChannel.lower()}:{author.lower()}'

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

    def __readJson(self, twitchChannel: str) -> ChatBandMember:
        if not utils.isValidStr(twitchChannel):
            raise ValueError(f'twitchChannel argument is malformed: \"{twitchChannel}\"')

        jsonContents = self.__readAllJson()
        if not utils.hasItems(jsonContents):
            return None

        for key in jsonContents:
            if key.lower() == twitchChannel.lower():
                return jsonContents[key]

        return None

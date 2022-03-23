import json
from datetime import timedelta
from os import path
from typing import Dict

try:
    import CynanBotCommon.utils as utils
    from CynanBotCommon.chatBand.chatBandInstrument import ChatBandInstrument
    from CynanBotCommon.chatBand.chatBandMember import ChatBandMember
    from CynanBotCommon.timber.timber import Timber
    from CynanBotCommon.timedDict import TimedDict
    from CynanBotCommon.websocketConnection.websocketConnectionServer import \
        WebsocketConnectionServer
except:
    import utils
    from timber.timber import Timber
    from timedDict import TimedDict
    from websocketConnection.websocketConnectionServer import \
        WebsocketConnectionServer

    from chatBand.chatBandInstrument import ChatBandInstrument
    from chatBand.chatBandMember import ChatBandMember


class ChatBandManager():

    def __init__(
        self,
        timber: Timber,
        websocketConnectionServer: WebsocketConnectionServer,
        chatBandFile: str = 'CynanBotCommon/chatBand/chatBandManager.json',
        eventType: str = 'chatBand',
        eventCooldown: timedelta = timedelta(minutes = 5),
        memberCacheTimeToLive: timedelta = timedelta(minutes = 15)
    ):
        if timber is None:
            raise ValueError(f'timber argument is malformed: \"{timber}\"')
        elif websocketConnectionServer is None:
            raise ValueError(f'websocketConnectionServer argument is malformed: \"{websocketConnectionServer}\"')
        elif not utils.isValidStr(chatBandFile):
            raise ValueError(f'chatBandFile argument is malformed: \"{chatBandFile}\"')
        elif not utils.isValidStr(eventType):
            raise ValueError(f'eventType argument is malformed: \"{eventType}\"')
        elif eventCooldown is None:
            raise ValueError(f'eventCooldown argument is malformed: \"{eventCooldown}\"')
        elif memberCacheTimeToLive is None:
            raise ValueError(f'memberCacheTimeToLive argument is malformed: \"{memberCacheTimeToLive}\"')

        self.__timber: Timber = timber
        self.__websocketConnectionServer: WebsocketConnectionServer = websocketConnectionServer
        self.__chatBandFile: str = chatBandFile
        self.__eventType: str = eventType
        self.__lastChatBandMessageTimes: TimedDict = TimedDict(eventCooldown)
        self.__chatBandMemberCache: TimedDict = TimedDict(memberCacheTimeToLive)
        self.__stubChatBandMember: ChatBandMember = ChatBandMember(False, ChatBandInstrument.BASS, "stub", "stub")

    def clearCaches(self):
        self.__lastChatBandMessageTimes.clear()
        self.__chatBandMemberCache.clear()
        self.__timber.log('ChatBandManager', 'Caches cleared')

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

        isDebugLoggingEnabled = self.__isDebugLoggingEnabled()
        chatBandMember: ChatBandMember = self.__chatBandMemberCache[self.__getCooldownKey(twitchChannel, author)]

        if chatBandMember is None:
            jsonContents = self.__readJsonForTwitchChannel(twitchChannel)

            if utils.hasItems(jsonContents):
                for key in jsonContents:
                    if key.lower() == author.lower():
                        chatBandMemberJson = jsonContents[key]

                        chatBandMember = ChatBandMember(
                            isEnabled = utils.getBoolFromDict(chatBandMemberJson, 'isEnabled', fallback = True),
                            instrument = ChatBandInstrument.fromStr(utils.getStrFromDict(chatBandMemberJson, 'instrument')),
                            author = key,
                            keyPhrase = utils.getStrFromDict(chatBandMemberJson, 'keyPhrase')
                        )

                        self.__chatBandMemberCache[self.__getCooldownKey(twitchChannel, author)] = chatBandMember

                        if isDebugLoggingEnabled:
                            self.__timber.log('ChatBandManager', f'Saving \"{twitchChannel}\" chat band member in cache: {self.__toEventData(chatBandMember)}')

                        break

        if chatBandMember is None:
            self.__chatBandMemberCache[self.__getCooldownKey(twitchChannel, author)] = self.__stubChatBandMember

        if chatBandMember is not None and chatBandMember is not self.__stubChatBandMember and chatBandMember.isEnabled() and chatBandMember.getKeyPhrase() == message:
            if isDebugLoggingEnabled:
                self.__timber.log('ChatBandManager', f'Found corresponding \"{twitchChannel}\" chat band member for given message: {self.__toEventData(chatBandMember)}')

            return chatBandMember
        else:
            return None

    def __getCooldownKey(self, twitchChannel: str, author: str) -> str:
        if not utils.isValidStr(twitchChannel):
            raise ValueError(f'twitchChannel argument is malformed: \"{twitchChannel}\"')
        elif not utils.isValidStr(author):
            raise ValueError(f'author argument is malformed: \"{author}\"')

        return f'{twitchChannel.lower()}:{author.lower()}'

    def __isDebugLoggingEnabled(self) -> bool:
        jsonContents = self.__readAllJson()
        return utils.getBoolFromDict(jsonContents, 'debugLoggingEnabled', fallback = False)

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

        if self.__isDebugLoggingEnabled():
            self.__timber.log('ChatBandManager', f'New \"{twitchChannel}\" Chat Band event: {self.__toEventData(chatBandMember)}')

        await self.__websocketConnectionServer.sendEvent(
            twitchChannel = twitchChannel,
            eventType = self.__eventType,
            eventData = self.__toEventData(chatBandMember)
        )

        return True

    def __readAllJson(self) -> Dict[str, object]:
        if not path.exists(self.__chatBandFile):
            raise FileNotFoundError(f'Chat Band file not found: \"{self.__chatBandFile}\"')

        with open(self.__chatBandFile, 'r') as file:
            jsonContents = json.load(file)

        if jsonContents is None:
            raise IOError(f'Error reading from Chat Band file: \"{self.__chatBandFile}\"')
        elif len(jsonContents) == 0:
            raise ValueError(f'JSON contents of Chat Band file \"{self.__chatBandFile}\" is empty')

        return jsonContents

    def __readJsonForTwitchChannel(self, twitchChannel: str) -> Dict[str, object]:
        if not utils.isValidStr(twitchChannel):
            raise ValueError(f'twitchChannel argument is malformed: \"{twitchChannel}\"')

        jsonContents = self.__readAllJson()
        twitchChannelsJson: Dict[str, object] = jsonContents.get('twitchChannels')
        if not utils.hasItems(twitchChannelsJson):
            raise ValueError(f'\"twitchChannels\" JSON contents of Chat Band file \"{self.__chatBandFile}\" is missing/empty')

        for key in twitchChannelsJson:
            if key.lower() == twitchChannel.lower():
                return twitchChannelsJson[key]

        return None

    def __toEventData(self, chatBandMember: ChatBandMember) -> Dict[str, object]:
        if chatBandMember is None:
            raise ValueError(f'chatBandMember argument is malformed: \"{chatBandMember}\"')

        return {
            'author': chatBandMember.getAuthor(),
            'instrument': chatBandMember.getInstrument().toStr(),
            'keyPhrase': chatBandMember.getKeyPhrase()
        }

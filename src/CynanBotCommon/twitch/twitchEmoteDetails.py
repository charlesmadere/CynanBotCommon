from typing import List, Optional

try:
    import CynanBotCommon.utils as utils
    from CynanBotCommon.twitch.twitchEmoteImage import TwitchEmoteImage
    from CynanBotCommon.twitch.twitchEmoteImageScale import \
        TwitchEmoteImageScale
    from CynanBotCommon.twitch.twitchEmoteType import TwitchEmoteType
    from CynanBotCommon.twitch.twitchSubscriberTier import TwitchSubscriberTier
except:
    import utils

    from twitch.twitchEmoteImage import TwitchEmoteImage
    from twitch.twitchEmoteImageScale import TwitchEmoteImageScale
    from twitch.twitchEmoteType import TwitchEmoteType
    from twitch.twitchSubscriberTier import TwitchSubscriberTier


class TwitchEmoteDetails():

    def __init__(
        self,
        emoteImages: List[TwitchEmoteImage],
        emoteId: str,
        emoteName: str,
        emoteType: TwitchEmoteType,
        subscriberTier: TwitchSubscriberTier
    ):
        if not utils.hasItems(emoteImages):
            raise ValueError(f'emoteImages argument is malformed: \"{emoteImages}\"')
        elif not utils.isValidStr(emoteId):
            raise ValueError(f'emoteId argument is malformed: \"{emoteId}\"')
        elif not utils.isValidStr(emoteName):
            raise ValueError(f'emoteName argument is malformed: \"{emoteName}\"')
        elif not isinstance(emoteType, TwitchEmoteType):
            raise ValueError(f'emoteType argument is malformed: \"{emoteType}\"')
        elif not isinstance(subscriberTier, TwitchSubscriberTier):
            raise ValueError(f'subscriberTier argument is malformed: \"{subscriberTier}\"')

        self.__emoteImages: List[TwitchEmoteImage] = emoteImages
        self.__emoteId: str = emoteId
        self.__emoteName: str = emoteName
        self.__emoteType: TwitchEmoteType = emoteType
        self.__subscriberTier: TwitchSubscriberTier = subscriberTier

    def getEmote(self, imageScale: TwitchEmoteImageScale) -> Optional[TwitchEmoteImage]:
        if not isinstance(imageScale, TwitchEmoteImageScale):
            raise ValueError(f'imageScale argument is malformed: \"{imageScale}\"')

        for emoteImage in self.__emoteImages:
            if emoteImage.getImageScale() is imageScale:
                return emoteImage

        return None

    def getEmotes(self) -> List[TwitchEmoteImage]:
        return self.__emoteImages

    def getEmoteId(self) -> str:
        return self.__emoteId

    def getEmoteName(self) -> str:
        return self.__emoteName

    def getEmoteType(self) -> TwitchEmoteType:
        return self.__emoteType

    def getSubscriberTier(self) -> TwitchSubscriberTier:
        return self.__subscriberTier

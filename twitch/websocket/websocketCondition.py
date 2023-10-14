from typing import Optional

try:
    import CynanBotCommon.utils as utils
    from CynanBotCommon.twitch.twitchSubscriberTier import TwitchSubscriberTier
except:
    import utils

    from twitch.twitchSubscriberTier import TwitchSubscriberTier


class WebsocketCondition():

    def __init__(
        self,
        isAnonymous: Optional[bool] = None,
        isGift: Optional[bool] = None,
        isPermanent: Optional[bool] = None,
        bits: Optional[int] = None,
        cumulativeTotal: Optional[int] = None,
        total: Optional[int] = None,
        viewers: Optional[int] = None,
        broadcasterUserId: Optional[str] = None,
        broadcasterUserLogin: Optional[str] = None,
        broadcasterUserName: Optional[str] = None,
        categoryId: Optional[str] = None,
        categoryName: Optional[str] = None,
        clientId: Optional[str] = None,
        fromBroadcasterUserId: Optional[str] = None,
        fromBroadcasterUserLogin: Optional[str] = None,
        fromBroadcasterUserName: Optional[str] = None,
        message: Optional[str] = None,
        moderatorUserId: Optional[str] = None,
        moderatorUserLogin: Optional[str] = None,
        moderatorUserName: Optional[str] = None,
        reason: Optional[str] = None,
        rewardId: Optional[str] = None,
        title: Optional[str] = None,
        toBroadcasterUserId: Optional[str] = None,
        toBroadcasterUserLogin: Optional[str] = None,
        toBroadcasterUserName: Optional[str] = None,
        userId: Optional[str] = None,
        userLogin: Optional[str] = None,
        userName: Optional[str] = None,
        tier: Optional[TwitchSubscriberTier] = None
    ):
        if isAnonymous is not None and not utils.isValidBool(isAnonymous):
            raise ValueError(f'isAnonymous argument is malformed: \"{isAnonymous}\"')
        elif isGift is not None and not utils.isValidBool(isGift):
            raise ValueError(f'isGift argument is malformed: \"{isGift}\"')
        elif isPermanent is not None and not utils.isValidBool(isPermanent):
            raise ValueError(f'isPermanent argument is malformed: \"{isPermanent}\"')
        elif bits is not None and not utils.isValidInt(bits):
            raise ValueError(f'bits argument is malformed: \"{bits}\"')
        elif cumulativeTotal is not None and not utils.isValidInt(cumulativeTotal):
            raise ValueError(f'cumulativeTotal argument is malformed: \"{cumulativeTotal}\"')
        elif total is not None and not utils.isValidInt(total):
            raise ValueError(f'total argument is malformed: \"{total}\"')
        elif viewers is not None and not utils.isValidInt(viewers):
            raise ValueError(f'viewers argument is malformed: \"{viewers}\"')
        if broadcasterUserId is not None and not isinstance(broadcasterUserId, str):
            raise ValueError(f'broadcasterUserId argument is malformed: \"{broadcasterUserId}\"')
        if broadcasterUserLogin is not None and not isinstance(broadcasterUserLogin, str):
            raise ValueError(f'broadcasterUserLogin argument is malformed: \"{broadcasterUserLogin}\"')
        if broadcasterUserName is not None and not isinstance(broadcasterUserName, str):
            raise ValueError(f'broadcasterUserName argument is malformed: \"{broadcasterUserName}\"')
        elif categoryId is not None and not isinstance(categoryId, str):
            raise ValueError(f'categoryId argument is malformed: \"{categoryId}\"')
        elif categoryName is not None and not isinstance(categoryName, str):
            raise ValueError(f'categoryName argument is malformed: \"{categoryName}\"')
        elif clientId is not None and not isinstance(clientId, str):
            raise ValueError(f'clientId argument is malformed: \"{clientId}\"')
        elif fromBroadcasterUserId is not None and not isinstance(fromBroadcasterUserId, str):
            raise ValueError(f'fromBroadcasterUserId argument is malformed: \"{fromBroadcasterUserId}\"')
        elif fromBroadcasterUserLogin is not None and not isinstance(fromBroadcasterUserLogin, str):
            raise ValueError(f'fromBroadcasterUserLogin argument is malformed: \"{fromBroadcasterUserLogin}\"')
        elif fromBroadcasterUserName is not None and not isinstance(fromBroadcasterUserName, str):
            raise ValueError(f'fromBroadcasterUserName argument is malformed: \"{fromBroadcasterUserName}\"')
        elif message is not None and not isinstance(message, str):
            raise ValueError(f'message argument is malformed: \"{message}\"')
        elif moderatorUserId is not None and not isinstance(moderatorUserId, str):
            raise ValueError(f'moderatorUserId argument is malformed: \"{moderatorUserId}\"')
        elif moderatorUserLogin is not None and not isinstance(moderatorUserLogin, str):
            raise ValueError(f'moderatorUserLogin argument is malformed: \"{moderatorUserLogin}\"')
        elif moderatorUserName is not None and not isinstance(moderatorUserName, str):
            raise ValueError(f'moderatorUserName argument is malformed: \"{moderatorUserName}\"')
        elif reason is not None and not isinstance(reason, str):
            raise ValueError(f'reason argument is malformed: \"{reason}\"')
        elif rewardId is not None and not isinstance(rewardId, str):
            raise ValueError(f'rewardId argument is malformed: \"{rewardId}\"')
        elif title is not None and not isinstance(title, str):
            raise ValueError(f'title argument is malformed: \"{title}\"')
        elif toBroadcasterUserId is not None and not isinstance(toBroadcasterUserId, str):
            raise ValueError(f'toBroadcasterUserId argument is malformed: \"{toBroadcasterUserId}\"')
        elif toBroadcasterUserLogin is not None and not isinstance(toBroadcasterUserLogin, str):
            raise ValueError(f'toBroadcasterUserLogin argument is malformed: \"{toBroadcasterUserLogin}\"')
        elif toBroadcasterUserName is not None and not isinstance(toBroadcasterUserName, str):
            raise ValueError(f'toBroadcasterUserName argument is malformed: \"{toBroadcasterUserName}\"')
        elif userId is not None and not isinstance(userId, str):
            raise ValueError(f'userId argument is malformed: \"{userId}\"')
        elif userLogin is not None and not isinstance(userLogin, str):
            raise ValueError(f'userLogin argument is malformed: \"{userLogin}\"')
        elif userName is not None and not isinstance(userName, str):
            raise ValueError(f'userName argument is malformed: \"{userName}\"')
        elif tier is not None and not isinstance(tier, TwitchSubscriberTier):
            raise ValueError(f'tier argument is malformed: \"{tier}\"')

        self.__isAnonymous: Optional[bool] = isAnonymous
        self.__isGift: Optional[bool] = isGift
        self.__isPermanent: Optional[bool] = isPermanent
        self.__bits: Optional[int] = bits
        self.__cumulativeTotal: Optional[int] = cumulativeTotal
        self.__total: Optional[int] = total
        self.__viewers: Optional[int] = viewers
        self.__broadcasterUserId: Optional[str] = broadcasterUserId
        self.__broadcasterUserLogin: Optional[str] = broadcasterUserLogin
        self.__broadcasterUserName: Optional[str] = broadcasterUserName
        self.__categoryId: Optional[str] = categoryId
        self.__categoryName: Optional[str] = categoryName
        self.__clientId: Optional[str] = clientId
        self.__fromBroadcasterUserId: Optional[str] = fromBroadcasterUserId
        self.__fromBroadcasterUserLogin: Optional[str] = fromBroadcasterUserLogin
        self.__fromBroadcasterUserName: Optional[str] = fromBroadcasterUserName
        self.__message: Optional[str] = message
        self.__moderatorUserId: Optional[str] = moderatorUserId
        self.__moderatorUserLogin: Optional[str] = moderatorUserLogin
        self.__moderatorUserName: Optional[str] = moderatorUserName
        self.__reason: Optional[str] = reason
        self.__rewardId: Optional[str] = rewardId
        self.__title: Optional[str] = title
        self.__toBroadcasterUserId: Optional[str] = toBroadcasterUserId
        self.__toBroadcasterUserLogin: Optional[str] = toBroadcasterUserLogin
        self.__toBroadcasterUserName: Optional[str] = toBroadcasterUserName
        self.__userId: Optional[str] = userId
        self.__userLogin: Optional[str] = userLogin
        self.__userName: Optional[str] = userName
        self.__tier: Optional[TwitchSubscriberTier] = tier

    def getBits(self) -> Optional[int]:
        return self.__bits

    def getBroadcasterUserId(self) -> Optional[str]:
        return self.__broadcasterUserId

    def getBroadcasterUserLogin(self) -> Optional[str]:
        return self.__broadcasterUserLogin

    def getBroadcasterUserName(self) -> Optional[str]:
        return self.__broadcasterUserName

    def getCategoryId(self) -> Optional[str]:
        return self.__categoryId

    def getCategoryName(self) -> Optional[str]:
        return self.__categoryName

    def getClientId(self) -> Optional[str]:
        return self.__clientId

    def getCumulativeTotal(self) -> Optional[int]:
        return self.__cumulativeTotal

    def getFromBroadcasterUserId(self) -> Optional[str]:
        return self.__fromBroadcasterUserId

    def getFromBroadcasterUserLogin(self) -> Optional[str]:
        return self.__fromBroadcasterUserLogin

    def getFromBroadcasterUserName(self) -> Optional[str]:
        return self.__fromBroadcasterUserName

    def getMessage(self) -> Optional[str]:
        return self.__message

    def getModeratorUserId(self) -> Optional[str]:
        return self.__moderatorUserId

    def getModeratorUserLogin(self) -> Optional[str]:
        return self.__moderatorUserLogin

    def getModeratorUserName(self) -> Optional[str]:
        return self.__moderatorUserName

    def getReason(self) -> Optional[str]:
        return self.__reason

    def getRewardId(self) -> Optional[str]:
        return self.__rewardId

    def getTier(self) -> Optional[TwitchSubscriberTier]:
        return self.__tier

    def getTitle(self) -> Optional[str]:
        return self.__title

    def getToBroadcasterUserId(self) -> Optional[str]:
        return self.__toBroadcasterUserId

    def getToBroadcasterUserLogin(self) -> Optional[str]:
        return self.__toBroadcasterUserLogin

    def getToBroadcasterUserName(self) -> Optional[str]:
        return self.__toBroadcasterUserName

    def getTotal(self) -> Optional[int]:
        return self.__total

    def getUserId(self) -> Optional[str]:
        return self.__userId

    def getUserLogin(self) -> Optional[str]:
        return self.__userLogin

    def getUserName(self) -> Optional[str]:
        return self.__userName

    def getViewers(self) -> Optional[int]:
        return self.__viewers

    def isAnonymous(self) -> Optional[bool]:
        return self.__isAnonymous

    def isGift(self) -> Optional[bool]:
        return self.__isGift

    def isPermanent(self) -> Optional[bool]:
        return self.__isPermanent

    def requireBroadcasterUserId(self) -> str:
        broadcasterUserId = self.__broadcasterUserId

        if not utils.isValidStr(broadcasterUserId):
            raise ValueError(f'broadcasterUserId has not been set: \"{broadcasterUserId}\"')

        return broadcasterUserId

from typing import Optional

try:
    import CynanBotCommon.utils as utils
    from CynanBotCommon.emojiHelper.emojiHelperInterface import \
        EmojiHelperInterface
    from CynanBotCommon.emojiHelper.emojiRepositoryInterface import \
        EmojiRepositoryInterface
except:
    import utils
    from emojiHelper.emojiHelperInterface import EmojiHelperInterface
    from emojiHelper.emojiRepositoryInterface import EmojiRepositoryInterface


class EmojiHelper(EmojiHelperInterface):

    def __init__(
        self,
        emojiRepository: EmojiRepositoryInterface
    ):
        if not isinstance(emojiRepository, EmojiRepositoryInterface):
            raise ValueError(f'emojiRepository argument is malformed: \"{emojiRepository}\"')

        self.__emojiRepository: EmojiRepositoryInterface = emojiRepository

    async def getHumanNameForEmoji(self, emoji: Optional[str]) -> Optional[str]:
        if not utils.isValidStr(emoji):
            return None

        emojiInfo = await self.__emojiRepository.fetchEmojiInfo(emoji)

        if emojiInfo is None:
            return None
        else:
            return emojiInfo.getName()

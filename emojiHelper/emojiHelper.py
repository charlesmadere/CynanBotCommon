from typing import Optional

import emoji

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

    async def replaceEmojisWithHumanNames(self, text: str) -> str:
        if not utils.isValidStr(text):
            raise ValueError(f'text argument is malformed: \"{text}\"')

        splits = utils.getCleanedSplits(text)

        if len(splits) == 0:
            return text

        replacementMade = False

        for index, split in enumerate(splits):
            if not emoji.is_emoji(split):
                continue

            replacementMade = True
            humanName = await self.getHumanNameForEmoji(split)

            if humanName is None:
                splits[index] = ''
            else:
                splits[index] = humanName

        if replacementMade:
            return ' '.join(splits).strip()
        else:
            return text
from abc import ABC, abstractmethod
from typing import Optional

try:
    from CynanBotCommon.emojiHelper.emojiInfo import EmojiInfo
except:
    from emojiHelper.emojiInfo import EmojiInfo


class EmojiRepositoryInterface(ABC):

    @abstractmethod
    async def fetchEmojiInfo(self, emoji: Optional[str]) -> Optional[EmojiInfo]:
        pass

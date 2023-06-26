from typing import Set

try:
    from CynanBotCommon.trivia.bannedWords.bannedWord import BannedWord
except:
    from trivia.bannedWords.bannedWord import BannedWord


class BannedWordsRepositoryInterface():

    async def clearCaches(self):
        pass

    def getBannedWords(self) -> Set[BannedWord]:
        pass

    async def getBannedWordsAsync(self) -> Set[BannedWord]:
        pass

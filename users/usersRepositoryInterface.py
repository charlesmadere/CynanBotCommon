from typing import List

try:
    from CynanBotCommon.users.userInterface import UserInterface
except:
    from users.userInterface import UserInterface


class UsersRepositoryInterface():

    async def clearCaches(self):
        pass

    def containsUser(self, handle: str) -> bool:
        pass

    async def containsUserAsync(self, handle: str) -> bool:
        pass

    def getUser(self, handle: str) -> UserInterface:
        pass

    async def getUserAsync(self, handle: str) -> UserInterface:
        pass

    def getUsers(self) -> List[UserInterface]:
        pass

    async def getUsersAsync(self) -> List[UserInterface]:
        pass

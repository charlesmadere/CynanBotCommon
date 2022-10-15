from typing import List

try:
    from CynanBotCommon.users.userInterface import UserInterface
except:
    from users.userInterface import UserInterface


class UsersRepositoryInterface():

    def getUser(self, handle: str) -> UserInterface:
        pass

    async def getUserAsync(self, handle: str) -> UserInterface:
        pass

    def getUsers(self) -> List[UserInterface]:
        pass

    async def getUsersAsync(self) -> List[UserInterface]:
        pass

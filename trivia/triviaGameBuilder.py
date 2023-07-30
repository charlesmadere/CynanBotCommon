try:
    import CynanBotCommon.utils as utils
    from CynanBotCommon.trivia.newSuperTriviaGameEvent import \
        NewSuperTriviaGameEvent
    from CynanBotCommon.trivia.newTriviaGameEvent import NewTriviaGameEvent
    from CynanBotCommon.trivia.triviaGameBuilderInterface import \
        TriviaGameBuilderInterface
    from CynanBotCommon.trivia.triviaGameBuilderSettingsInterface import \
        TriviaGameBuilderSettingsInterface
    from CynanBotCommon.users.usersRepositoryInterface import \
        UsersRepositoryInterface
except:
    import utils
    from trivia.newSuperTriviaGameEvent import NewSuperTriviaGameEvent
    from trivia.newTriviaGameEvent import NewTriviaGameEvent
    from trivia.triviaGameBuilderInterface import TriviaGameBuilderInterface
    from trivia.triviaGameBuilderSettingsInterface import \
        TriviaGameBuilderSettingsInterface

    from users.usersRepositoryInterface import UsersRepositoryInterface


class TriviaGameBuilder(TriviaGameBuilderInterface):

    def __init__(
        self,
        triviaGameBuilderSettings: TriviaGameBuilderSettingsInterface,
        usersRepository: UsersRepositoryInterface
    ):
        if not isinstance(triviaGameBuilderSettings, TriviaGameBuilderSettingsInterface):
            raise ValueError(f'triviaGameBuilderSettings argument is malformed: \"{triviaGameBuilderSettings}\"')
        if not isinstance(usersRepository, UsersRepositoryInterface):
            raise ValueError(f'usersRepository argument is malformed: \"{usersRepository}\"')

        self.__triviaGameBuilderSettings: TriviaGameBuilderSettingsInterface = triviaGameBuilderSettings
        self.__usersRepository: UsersRepositoryInterface = usersRepository

    async def createNewSuperTriviaGame(self, twitchChannel: str) -> NewSuperTriviaGameEvent:
        if not utils.isValidStr(twitchChannel):
            raise ValueError(f'twitchChannel argument is malformed: \"{twitchChannel}\"')

        user = await self.__usersRepository.getUserAsync(twitchChannel)

        if not user.isTriviaGameEnabled() or not user.isSuperTriviaGameEnabled():
            return

        # TODO
        pass

    async def createNewTriviaGame(self, twitchChannel: str) -> NewTriviaGameEvent:
        if not utils.isValidStr(twitchChannel):
            raise ValueError(f'twitchChannel argument is malformed: \"{twitchChannel}\"')

        user = await self.__usersRepository.getUserAsync(twitchChannel)

        if not user.isTriviaGameEnabled():
            return

        # TODO
        pass

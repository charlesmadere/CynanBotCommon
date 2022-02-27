from datetime import datetime, timezone

try:
    import CynanBotCommon.utils as utils
    from CynanBotCommon.trivia.absTriviaQuestion import AbsTriviaQuestion
except:
    import utils

    from trivia.absTriviaQuestion import AbsTriviaQuestion


class TriviaGameState():

    def __init__(self, twitchChannel: str):
        if not utils.isValidStr(twitchChannel):
            raise ValueError(f'twitchChannel argument is malformed: \"{twitchChannel}\"')

        self.__triviaQuestion: AbsTriviaQuestion = None
        self.__isAnswered: bool = None
        self.__answerTime: datetime = None
        self.__twitchChannel: str = twitchChannel
        self.__userIdThatRedeemed: str = None
        self.__userNameThatRedeemed: str = None

    def getAnswerTime(self) -> datetime:
        return self.__answerTime

    def getTriviaQuestion(self) -> AbsTriviaQuestion:
        return self.__triviaQuestion

    def getTwitchChannel(self) -> str:
        return self.__twitchChannel

    def getUserIdThatRedeemed(self) -> str:
        return self.__userIdThatRedeemed

    def getUserNameThatRedeemed(self) -> str:
        return self.__userNameThatRedeemed

    def isAnswered(self) -> bool:
        isAnswered = self.__isAnswered
        return isAnswered is None or isAnswered

    def setAnswered(self):
        self.__isAnswered = None
        self.__answerTime = None
        self.__userIdThatRedeemed = None
        self.__userNameThatRedeemed = None

    def setTriviaQuestion(self, triviaQuestion: AbsTriviaQuestion):
        if triviaQuestion is None:
            raise ValueError(f'triviaQuestion argument is malformed: \"{triviaQuestion}\"')

        self.__triviaQuestion = triviaQuestion

    def startNewTriviaGame(
        self,
        userIdThatRedeemed: str,
        userNameThatRedeemed: str
    ):
        if not utils.isValidStr(userIdThatRedeemed):
            raise ValueError(f'userIdThatRedeemed argument is malformed: \"{userIdThatRedeemed}\"')
        elif not utils.isValidStr(userNameThatRedeemed):
            raise ValueError(f'userNameThatRedeemed argument is malformed: \"{userNameThatRedeemed}\"')

        self.__isAnswered = False
        self.__answerTime = datetime.now(timezone.utc)
        self.__userIdThatRedeemed = userIdThatRedeemed
        self.__userNameThatRedeemed = userNameThatRedeemed

try:
    from CynanBotCommon.trivia.absTriviaAction import AbsTriviaAction
    from CynanBotCommon.trivia.triviaActionType import TriviaActionType
except:
    from trivia.absTriviaAction import AbsTriviaAction
    from trivia.triviaActionType import TriviaActionType


class CheckAnswerTriviaAction(AbsTriviaAction):

    def __init__(self, triviaActionType: TriviaActionType):
        super().__init__(triviaActionType)

from trivia.triviaAnswerCompiler import TriviaAnswerCompiler


class TestTriviaAnswerCompiler():

    def __init__(self):
        self.__triviaAnswerCompiler: TriviaAnswerCompiler = TriviaAnswerCompiler()

    def test_sanity(self):
        assert isinstance(self.__triviaAnswerCompiler, TriviaAnswerCompiler)

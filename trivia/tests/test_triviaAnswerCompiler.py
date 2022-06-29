try:
    from ...trivia.triviaAnswerCompiler import TriviaAnswerCompiler
except:
    from trivia.triviaAnswerCompiler import TriviaAnswerCompiler


class TestTriviaAnswerCompiler():

    __triviaAnswerCompiler: TriviaAnswerCompiler = TriviaAnswerCompiler()

    def test_sanity(self):
        assert isinstance(self.__triviaAnswerCompiler, TriviaAnswerCompiler)

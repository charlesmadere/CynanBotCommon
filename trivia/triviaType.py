from enum import Enum, auto

try:
    import CynanBotCommon.utils as utils
except:
    import utils


class TriviaType(Enum):

    MULTIPLE_CHOICE = auto()
    QUESTION_ANSWER = auto()
    TRUE_FALSE = auto()

    @classmethod
    def fromStr(cls, text: str):
        if not utils.isValidStr(text):
            raise ValueError(f'text argument is malformed: \"{text}\"')

        text = text.lower()

        if text == 'bool' or text == 'boolean' or text == 'true-false' or text == 'true_false' or text == 'true false':
            return TriviaType.TRUE_FALSE
        elif text == 'multiple' or text == 'multiple-choice' or text == 'multiple_choice' or text == 'multiple choice':
            return TriviaType.MULTIPLE_CHOICE
        elif text == 'question-answer' or text == 'question_answer' or text == 'question answer':
            return TriviaType.QUESTION_ANSWER
        else:
            raise ValueError(f'unknown TriviaType: \"{text}\"')

    def toStr(self) -> str:
        if self is TriviaType.MULTIPLE_CHOICE:
            return 'multiple-choice'
        elif self is TriviaType.QUESTION_ANSWER:
            return 'question-answer'
        elif self is TriviaType.TRUE_FALSE:
            return 'true-false'
        else:
            raise ValueError(f'unknown TriviaType: \"{self}\"')

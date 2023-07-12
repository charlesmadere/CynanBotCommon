from typing import Optional

try:
    from CynanBotCommon.recurringActions.recurringActionListener import \
        RecurringActionListener
    from CynanBotCommon.recurringActions.recurringActionsHelperInterface import \
        RecurringActionsHelperInterface
except:
    from recurringActions.recurringActionListener import \
        RecurringActionListener
    from recurringActions.recurringActionsHelperInterface import \
        RecurringActionsHelperInterface


class RecurringActionsHelper(RecurringActionsHelperInterface):

    def __init__(self):
        self.__actionListener: Optional[RecurringActionListener] = None

    def setRecurringActionListener(self, listener: Optional[RecurringActionListener]):
        if listener is not None and not isinstance(listener, RecurringActionListener):
            raise ValueError(f'listener argument is malformed: \"{listener}\"')

        self.__actionListener = listener

    def startRecurringActions(self):
        # TODO
        pass

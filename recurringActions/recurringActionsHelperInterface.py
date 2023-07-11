from abc import abstractmethod


class RecurringActionsHelperInterface():

    def __init__(self):
        pass

    @abstractmethod
    def startRecurringActions(self):
        pass

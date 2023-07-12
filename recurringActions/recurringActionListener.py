try:
    from CynanBotCommon.recurringActions.absRecurringAction import \
        AbsRecurringAction
except:
    from recurringActions.absRecurringAction import AbsRecurringAction


class RecurringActionListener():

    async def onNewRecurringAction(self, action: AbsRecurringAction):
        pass

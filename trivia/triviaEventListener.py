try:
    from CynanBotCommon.trivia.absTriviaEvent import AbsTriviaEvent
except:
    from trivia.absTriviaEvent import AbsTriviaEvent


class TriviaEventListener():

    async def onNewTriviaEvent(self, event: AbsTriviaEvent):
        pass

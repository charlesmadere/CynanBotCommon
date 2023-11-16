import uuid

try:
    from CynanBotCommon.cheerActions.cheerActionIdGeneratorInterface import \
        CheerActionIdGeneratorInterface
except:
    from cheerActions.cheerActionIdGeneratorInterface import \
        CheerActionIdGeneratorInterface


class CheerActionIdGenerator(CheerActionIdGeneratorInterface):

    async def generateActionId(self) -> str:
        return str(uuid.uuid4())

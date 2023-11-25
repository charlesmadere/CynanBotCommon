from abc import ABC, abstractmethod

try:
    from CynanBotCommon.language.jishoResult import JishoResult
except:
    from language.jishoResult import JishoResult


class JishoHelperInterface(ABC):

    @abstractmethod
    async def search(self, query: str) -> JishoResult:
        pass

from abc import abstractmethod
from typing import Optional


class TimberInterface():

    @abstractmethod
    def log(
        self,
        tag: str,
        msg: str,
        exception: Optional[Exception] = None,
        traceback: Optional[str] = None
    ):
        pass

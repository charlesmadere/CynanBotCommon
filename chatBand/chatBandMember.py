try:
    import CynanBotCommon.utils as utils
    from CynanBotCommon.chatBand.chatBandInstrument import ChatBandInstrument
except:
    import utils

    from chatBand.chatBandInstrument import ChatBandInstrument


class ChatBandMember():

    def __init__(
        self,
        instrument: ChatBandInstrument,
        author: str,
        keyPhrase: str
    ):
        if instrument is None:
            raise ValueError(f'instrument argument is malformed: \"{instrument}\"')
        elif not utils.isValidStr(author):
            raise ValueError(f'author argument is malformed: \"{author}\"')
        elif not utils.isValidStr(keyPhrase):
            raise ValueError(f'keyPhrase argument is malformed: \"{keyPhrase}\"')

        self.__instrument: ChatBandInstrument = instrument
        self.__author: str = author
        self.__keyPhrase: str = keyPhrase

    def getAuthor(self) -> str:
        return self.__author

    def getInstrument(self) -> ChatBandInstrument:
        return self.__instrument

    def getKeyPhrase(self) -> str:
        return self.__keyPhrase

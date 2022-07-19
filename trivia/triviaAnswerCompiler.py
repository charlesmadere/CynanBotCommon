import re
from typing import List, Pattern, Set

import roman
from num2words import num2words

try:
    import CynanBotCommon.utils as utils
    from CynanBotCommon.trivia.triviaExceptions import BadTriviaAnswerException
except:
    import utils

    from trivia.triviaExceptions import BadTriviaAnswerException


class TriviaAnswerCompiler():

    def __init__(self):
        self.__ampersandRegEx: Pattern = re.compile(r'(^&\s+)|(\s+&\s+)|(\s+&$)', re.IGNORECASE)
        self.__multipleChoiceAnswerRegEx: Pattern = re.compile(r'[a-z]', re.IGNORECASE)
        self.__newLineRegEx: Pattern = re.compile(r'(\n)+', re.IGNORECASE)
        self.__parenGroupRegEx: Pattern = re.compile(r'(\(.*?\))', re.IGNORECASE)
        self.__phraseAnswerRegEx: Pattern = re.compile(r'[^A-Za-z0-9 ]|(?<=\s)\s+', re.IGNORECASE)
        self.__prefixRegEx: Pattern = re.compile(r'^(a|an|and|or|the)\s+', re.IGNORECASE)
        self.__tagRemovalRegEx: Pattern = re.compile(r'[<\[]\/?\w+[>\]]', re.IGNORECASE)
        self.__whiteSpaceRegEx: Pattern = re.compile(r'\s\s*', re.IGNORECASE)

        # RegEx pattern for arabic and roman numerals, returning only one capturing group
        self.__numeralRegEx: Pattern = re.compile(r'\b(\d+(?:st|nd|rd|th)?|[IVXLCDM]+(?:st|nd|rd|th)?)\b', re.IGNORECASE)
        # RegEx patterns for arabic and roman numerals, returning separate capturing groups for digits and ordinals
        self.__groupedNumeralRegEx: Pattern = re.compile(r'\b(?:(\d+)|([IVXLCDM]+))(st|nd|rd|th)?\b', re.IGNORECASE)

        self.__hashRegEx: Pattern = re.compile(r'(#)')
        self.__equationRegEx: Pattern = re.compile(r'([a-z])\s*=\s*(-?(?:\d*\.)?\d+)', re.IGNORECASE)

        self.__specialCharsRegEx: Pattern = re.compile(
            r"""
                (?P<a>[ÅåǺǻḀḁẚĂăẶặẮắẰằẲẳẴẵȂȃâẬậẤấẦầẪẫẨẩẢảǍǎȺⱥȦȧǠǡẠạÄäǞǟÀàȀȁÁáĀāÃãĄąᶏɑᶐⱯɐɒᴀᴬᵃᵄᶛₐªÅ∀@₳ΑαАаⲀⲁⒶⓐ⒜🅰𝔄𝔞𝕬𝖆𝓐𝓪𝒜𝒶𝔸𝕒Ａａ🄰ค𝐀𝐚𝗔𝗮𝘈𝘢𝘼𝙖𝙰𝚊Λ卂ﾑȺᗩΔልДдꚈꚉꚀꚁꙢꙣꭿꋫλ🅐🅰️ꙢꙣꙘѦԬꙙѧԭӒӓҨҩ])|
                (?P<b>[ΒβⲂⲃВвБб𐌁ᛒ𐌱ɓʙɃƀḂḃḄḅḆḇƁᵬᶀꞖꞗᴃᴯᴮᵇƂƃ␢฿₿♭𝐁𝐛𝔹𝕓𝕭𝖇𝑩𝒃🄱🅱️Ⓑⓑ🅑ᙠᗷҍ𝔅𝔟𝓑𝓫𝗕𝗯𝘽𝙗𝘉𝘣Ｂｂ⒝𝙱𝚋𝖡𝖻🇧๖乃𝑏ƄЬᏏᖯᑲ𝒷𝚩ꓐ𝜝𝛣𝝗𐊂𝞑ℬᏴ𐊡𝐵])|
                (?P<c>[СсɕʗᶜᶝᴄꟄꞔĆćĈĉČčĊċḈḉƇƈȻȼÇçꞒꞓↃↄ©℃¢₡₢₵₠ℂℭꜾꜿ𝑐𝗰ｃ𝕔ⲥ𐐽𝖈𝓬𝚌ꮯ𝔠ϲ𝒄𝘤𝒸𝙘𝐜𝖼ⅽ𝕮𝙲𝑪𝒞𝖢𐌂𝗖ꓚᏟＣⲤ𝓒Ⅽ𝘊𐐕𝘾🝌𝐂Ϲ𐊢𝐶])|
                (?P<d>[ԀԁƊɗ𝓭𝚍ⅆ𝑑𝗱Ꮷ𝒅𝘥𝖉ᑯꓒ𝐝𝖽𝔡𝕕ⅾ𝒹𝙙Ꭰ𝕯ⅅ𝓓𝙳𝔇ᗪ𝑫𝘋Ⅾ𝒟𝘿ꓓ𝐃𝖣𝐷𝗗𝔻ᗞ])|
                (?P<e>[ẹėéèеẸĖÉÈЕ𝓮𝚎ｅ𝑒𝗲ⅇ𝒆𝘦℮𝖊ℯ𝐞𝖾ꬲ𝔢𝕖ҽ𝙚𝙴𝛦𝑬𝚬𝜠𝖤Ε𝗘𐊆𝝚𝓔𝞔Ｅ𝔈𝘌Ꭼℰ𝙀ꓰⴹ])|
                (?P<f>[f𝓯𝚏𝑓𝗳𝒇𝘧𝖋𝐟𝖿𝔣ꬵ𝕗ꞙ𝒻𝙛ẝ𝕱Ꞙ𝓕Ϝ𐊇ꓝ𝗙ℱᖴ𝙁𝙵𐊥𝐹])|
                (?P<g>[ġĠ𝓰𝚐ɡցᶃ𝑔𝗴ｇ𝒈𝘨ℊ𝖌𝐠𝗀𝔤𝕘𝙜Ꮐ𝑮𝘎𝕲𝐆𝖦Ԍ𝔊𝔾Ᏻ𝒢𝙂ꓖ𝓖𝙶𝐺𝗚])|
                (?P<h>[һҺᏂ𝖍𝓱𝚑ｈ𝔥ℎ𝒉𝘩հ𝒽𝙝𝐡𝗁𝗵𝕙𝑯𝚮𝕳𝛨𝖧ℋℌℍⲎ𐋏𝜢Η𝓗𝞖𝝜𝗛Н𝘏ꓧＨ𝐇𝙃𝙷Ꮋᕼ𝐻])|
                (?P<i>[іíïІÍÏ𝓲𝞲ꙇⅈｉ𝔦𝘪ӏ𝙞𝚤𝐢𝑖𝕚𝖎Ꭵ𝚒ɩɪ𝒊𝛊ⅰı𝒾𝜾⍳𝜄ꭵ𝗂𝝸ℹι𝗶𝚰𝘭𝖨𝐥ﺍﺎ𝔩ℐℑ𐊊Ⲓ𐌉ℓ𝜤Ɩ𝞘Ι𝚕𝟏∣اＩ𝗅𝕀𝙄𝓁𐌠𝐼𝑰ǀӀᛁ𝟭𝕴ߊｌ𝛪ⵏ𝝞𝕝𝟣𝙡𝓘𝗜𝟙𝑙ןⅠ𝘐١𝒍𝖑￨𝐈۱ꓲ|ⅼ])|
                (?P<j>[јʝЈꞲ𝖏𝓳𝚓ⅉ𝔧ｊ𝒋𝘫𝒿𝙟ϳ𝐣𝗃𝑗𝗷𝕛𝔍𝑱𝘑Ｊ𝒥𝙅Ꭻᒍ𝐉𝖩𝐽𝗝𝕁ꓙ𝕵𝓙𝙹Ϳ])|
                (?P<k>[κΚ𝖐𝓴𝚔𝔨𝒌𝘬𝓀𝙠𝐤𝗄𝑘𝗸𝕜𝑲𝚱𝒦𝜥𝛫𝖪𝝟𝗞ⲔᛕꓗК𝓚𝞙𝔎𝘒Ꮶ𝙆Ｋ])|
                (?P<l>[ӏḷӀḶ𝚰𝘭І𝖨𝐥ﺍﺎ𝔩ℐℑ𐊊Ⲓ𐌉ℓ𝜤Ɩ𝞘Ι𝚕𝟏∣ا𝗅𝕀𝙄𝓁𐌠𝐼𝑰ǀᛁ𝟭𝕴ߊｌ𝛪ⵏ𝝞𝕝𝟣ו𞣇𝙡𝓘𝗜𝟙𝑙ןⅠ𝘐١𝒍𝖑𝐈۱|ⅼ𝖫Ⳑ𝗟ℒ𝓛Ꮮꓡ𐐛𝘓𝙇ᒪⅬ])|
                (?P<m>[m𝔪𝕞𝓂𝙢𝓶𝚖𝑚𝗺ⅿ𝛭𝑴𝚳𝜧𐌑𝖬𝗠ᛖ𝝡Ⲙ𝓜ΜМ𝞛ꓟ𝔐𝘔𝙈𐊰𝐌ＭⅯ𝑀ᗰℳ𝕄Ꮇ𝕸Ϻ𝙼])|
                (?P<n>[ոՈΝれり𝒏𝘯𝖓𝐧𝗇𝔫𝕟𝓃𝙣𝓷𝚗ռ𝑛𝗻ꓠ𝛮𝐍𝖭𝚴𝔑𝜨Ｎ𝒩𝙉𝓝𝙽ℕ𝝢𝑁𝗡Ⲛ𝑵𝘕𝞜𝕹])|
                (?P<o>[оᴏοօØøǾǿÖöȪȫÓóÒòÔôỐốỒồỔổỖỗỘộǑǒŐőŎŏȎȏȮȯȰȱỌọƟɵƠơỚớỜờỠỡỢợỞởỎỏŌōṒṓṐṑÕõȬȭṌṍṎṏǪǫȌȍǬǭꝌꝍⱺᴏᴼᵒᴑᴓꬽꬾꬿꭃꭄₒꝊꝋ∅ºΟοⲞⲟОо𐌏ՕօＯｏ◎Ⓞ⒪⓪⓿⍟Ꜿꜿ𝘰ంಂംං𝐨𐓪𝚘ဝ𝛐ഠ𝛔𝗈𝝈𝝄𝞸𝞼၀σ๐໐𝕠𐐬𝙤ە𝑜𝒐ס𝜎𝖔٥०੦૦௦౦೦൦𝜊𝝾۵𝞂𝓸𝗼ჿ߀𝛰〇𐊒𝟬𝒪𝜪ዐ𝓞𝞞𝝤ⵔ𝟢𝗢𝟘𝘖ଠ𝟎𝐎০୦𝔒𝕆𝙊𐊫𝙾ꓳ𐐄𝟶𝑶𝚶𐓂𝕺])|
                (?P<p>[рРρ𝔭𝘱𝙥𝐩ｐ𝛠𝑝𝕡𝖕𝜚𝚙𝞎ⲣ𝝔𝛒𝒑𝟈𝝆𝓅𝜌𝗉𝞀ϱ𝗽⍴𝞺𝓹𝖯𝛲𝝦𝜬𝒫𐊕𝞠𝓟ꓑ𝗣ℙ𝘗𝐏ΡⲢᏢ𝙋ᑭＰ𝙿𝑃𝚸𝑷])|
                (?P<q>[զԶ𝔮գ𝒒𝘲𝓆𝙦𝐪𝗊𝑞𝗾𝕢𝖖ԛ𝓺𝚚𝐐𝖰𝔔𝒬𝙌𝓠𝚀𝑄𝗤ⵕ𝑸𝘘ℚ𝕼])|
                (?P<r>[r𝔯ꮁ𝒓𝘳ⲅᴦꭇꭈ𝓇𝙧𝐫𝗋𝑟𝗿г𝕣𝖗𝓻𝚛ᎡꓣƦ𝐑𝖱ᖇ𐒴𝑅𝗥Ꮢ𝕽𝓡𝚁ℛℜℝ])|
                (?P<s>[ʂꟅꮪ𝐬𝗌𝑠𝘀ꜱｓ𝕤ѕ𝖘𝓼𝚜𐑈ƽ𝒮𝙎ꓢ𐐠Ѕ𝐒𝖲𝑆𝗦𐊖𝕊Տ𝕾ＳᏕ𝓢𝚂𝔖Ꮪ𝑺𝘚])|
                (?P<t>[𝐭𝗍𝔱𝕥𝓉𝙩𝓽𝚝𝑡𝘁𝒕𝘵𝖙𝒯𝜯𝖳𝗧𐊗𐌕𝝩🝨ꓔТᎢ⊤Τ𝐓Ⲧ𝑇𐊱𝕋Ｔ𝚃𝛵𝑻𝚻])|
                (?P<u>[υսüúùՍÜÚÙ𝐮𝔲ʋ𝙪ꭎ𐓶𝚞ꭒ𝑢𝒖𝛖ᴜ𝖚ꞟ𝜐𝗎𝓊𝝊𝓾𝞾𝞄𝘂𝘶𝒰𝙐ሀ⋃𝐔𝖴𝑈𝗨ᑌ𝖀𝓤𝚄ꓴ𐓎𝔘𝑼𝘜])|
                (?P<v>[νѵѴⱯ∀⋁𝐯𝔳𝕧𝙫𝚟𝑣ｖט𝒗𝖛ᴠ𝗏ꮩ𝓋𝓿ⅴ𝘃𝝂𝘷𝞶Ꮩ𝐕Ⅴꓦ٧𝙑ᐯ𝑽۷𝖁ⴸ𝖵])|
                (?P<w>[w𝐰𝗐ᴡѡաꮃ𝔴𝕨𝓌𝙬ɯ𝔀𝚠𝒘𝘸𝖜ԝ𝕎𝒲𝙒𝓦𝚆ꓪ𝑊𝗪ᎳᏔ𝖂𝐖𝖶Ԝ𝔚])|
                (?P<x>[хҳХҲᕁ𝓍𝙭𝐱𝗑⤫𝑥𝘅⤬᙮⨯𝕩𝖝×𝔁𝚡ｘⅹ𝔵ᕽ𝒙𝘹𝒳𝜲𝓧𝞦𐊐𝝬𐌗𝗫𝘟𝐗𝔛ⵝΧⅩ𝚇ꓫⲬ᙭𝑋𐊴𝑿𝚾╳Ꭓ𝖃ᚷＸ𝛸𐌢𝖷])|
                (?P<y>[уýУÝΥ𝙮𝐲𝝲𝑦ᶌ𝞬ʏ𝖞𝚢ｙꭚ𝒚𝓎ɣ𝗒ყ𝘆ү𝛾γ𝛄𝔂𝜸𝔶ℽ𝘺ỿϒ𝔜𝕐𝙔𝚈ⲨᎩ𐊲𝑌ꓬҮ𝒀𝖄𝖸Ｙ𝛶𝚼Ꮍ])|
                (?P<z>[ʐżŻ𝓏𝙯ᴢ𝐳𝗓ꮓ𝔃𝚣𝔷𝒛𝘻𝗭𝚭ᏃΖ𝘡𝜡𝙕𝞕ꓜ𝝛𝐙𝑍ℤℨ𝖅Ｚ𝒵𝖹])
            """,
            re.VERBOSE | re.IGNORECASE,
        )

        self.__combiningDiacriticsRegEx = re.compile(r'[\u0300-\u036f\u1ab0-\u1aff\u1dc0-\u1dff\u20d0-\u20ff\ufe20-\ufe2f]')

    async def compileBoolAnswer(self, answer: str) -> str:
        cleanedAnswer = await self.compileTextAnswer(answer)

        try:
            return utils.strToBool(cleanedAnswer)
        except ValueError:
            raise BadTriviaAnswerException(f'answer can\'t be compiled to bool (answer:{answer}) (cleanedAnswer:{cleanedAnswer})')

    async def compileTextAnswer(self, answer: str) -> str:
        if not utils.isValidStr(answer):
            return ''

        answer = answer.lower().strip()

        # removes HTML tag-like junk
        answer = self.__tagRemovalRegEx.sub('', answer).strip()

        # replaces all new line characters with just a space
        answer = self.__newLineRegEx.sub(' ', answer).strip()

        # removes common phrase prefixes
        answer = self.__prefixRegEx.sub('', answer).strip()

        # replaces the '&' character, when used like the word "and", with the word "and"
        answer = self.__ampersandRegEx.sub(' and ', answer).strip()

        # convert special characters to latin where possible
        answer = self.__fancyToLatin(answer)

        # removes all special characters
        answer = self.__phraseAnswerRegEx.sub('', answer).strip()

        return answer

    async def compileTextAnswersList(self, answers: List[str], expandParentheses: bool = True) -> List[str]:
        if not utils.hasItems(answers):
            return list()

        cleanedAnswers: Set[str] = set()

        for answer in answers:
            if not utils.isValidStr(answer):
                continue
            cases = await self.expandSpecialCases(answer)
            for case in cases:
                if expandParentheses:
                    possibilities = await self.__getParentheticalPossibilities(case)
                else:
                    possibilities = [case]

                for possibility in possibilities:
                    cleanedAnswer = await self.compileTextAnswer(possibility)
                    cleanedAnswers.add(self.__whiteSpaceRegEx.sub(' ', cleanedAnswer))

        return list(answer for answer in cleanedAnswers if utils.isValidStr(answer))

    async def expandSpecialCases(self, answer: str) -> List[str]:
        # expand 'X=5' to ['5', 'X = 5', 'X is 5', 'X equals 5']
        match = self.__equationRegEx.search(answer)
        if match:
            return [
                match.group(2),
                f'{match.group(1)} = {match.group(2)}',
                f'{match.group(1)} is {match.group(2)}',
                f'{match.group(1)} equals {match.group(2)}',
            ]

        # expand 'mambo #5' to ['mambo #5', 'mambo number 5']
        split = self.__hashRegEx.split(answer)
        for i in range(1, len(split), 2):
            split[i] = ['number ', '#']
        return [''.join(item) for item in utils.permuteSubArrays(split)]

    # returns text answers with all arabic and roman numerals expanded into possible full-word forms
    async def expandNumerals(self, answer: str) -> List[str]:
        split = self.__numeralRegEx.split(answer)
        for i in range(1, len(split), 2):
            match = self.__groupedNumeralRegEx.fullmatch(split[i])
            if not match:
                raise BadTriviaAnswerException(f'numbers cannot be expanded properly in trivia answer (answer: {answer})')
            if not match.group(1):
                # roman numerals
                split[i] = await self.__getRomanNumeralSubstitutes(match.group(2))
            else:
                # arabic numerals
                split[i] = await self.__getArabicNumeralSubstitutes(match.group(1))
        return list(set(''.join(item) for item in utils.permuteSubArrays(split)))

    async def compileTextAnswerToMultipleChoiceOrdinal(self, answer: str) -> int:
        cleanedAnswer = await self.compileTextAnswer(answer)

        if not utils.isValidStr(cleanedAnswer) or len(cleanedAnswer) != 1 or self.__multipleChoiceAnswerRegEx.fullmatch(cleanedAnswer) is None:
            raise BadTriviaAnswerException(f'answer can\'t be compiled to multiple choice ordinal (answer:{answer}) (cleanedAnswer:{cleanedAnswer})')

        # this converts the answer 'A' into 0, 'B' into 1, 'C' into 2, and so on...
        return ord(cleanedAnswer.upper()) % 65

    async def __getArabicNumeralSubstitutes(self, arabicNumerals: str) -> List[str]:
        individualDigits = ' '.join([num2words(int(digit)) for digit in arabicNumerals])
        n = int(arabicNumerals)
        return [
                num2words(n, to='ordinal').replace('-', ' ').replace(',', ''),
                'the ' + num2words(n, to='ordinal').replace('-', ' ').replace(',', ''),
                num2words(n).replace('-', ' ').replace(',', ''),
                num2words(n, to='year').replace('-', ' ').replace(',', ''),
                individualDigits,
            ]

    async def __getRomanNumeralSubstitutes(self, romanNumerals: str) -> List[str]:
        n = roman.fromRoman(romanNumerals.upper())
        return [
            romanNumerals.lower(),
            num2words(n, to='ordinal').replace('-', ' ').replace(',', ''),
            'the ' + num2words(n, to='ordinal').replace('-', ' ').replace(',', ''),
            num2words(n).replace('-', ' ').replace(',', ''),
            num2words(n, to='year').replace('-', ' ').replace(',', ''),
        ]

    # Returns all possibilities with parenthesized phrases both included and excluded
    async def __getParentheticalPossibilities(self, answer: str) -> List[str]:
        # Split the uncleaned answer with this regex to find all parentheticals
        splitPossibilities = self.__parenGroupRegEx.split(answer)

        # join the split possibilities back to strings and substitute multiple whitespaces back to a single space.
        return [ self.__whiteSpaceRegEx.sub(' ', ''.join(p).strip()) for p in await self.__getSubPossibilities(splitPossibilities) ]

    # Recursively resolves the possibilities for each word in the answer.
    async def __getSubPossibilities(self, splitAnswer: str) -> List[str]:
        # early exit on trivial cases
        if not len(splitAnswer):
            return [ ]
        if len(splitAnswer) == 1:
            return [ splitAnswer ]

        # get all "future" possible variants starting with the next word
        futurePossible = await self.__getSubPossibilities(splitAnswer[1:])

        # switch on open paren
        if splitAnswer[0].startswith('('):
            res = [ ]
            for possible in futurePossible:
                # add a version including this word but without the parentheses
                res.append([ splitAnswer[0][1:-1], *possible ])
                # also keep the version not including this word at all
                res.append(possible)
            # return all possibilities, with and without this word
            return res
        else:
            # return all future possibilities with this current word mapped onto it as well.
            return [ [ splitAnswer[0], *possible ] for possible in futurePossible ]

    def __fancyToLatin(self, text: str) -> str:
        text = ''.join(
            self.__specialCharsRegEx.sub(
                lambda m: {k: v for k, v in m.groupdict().items() if v}.popitem()[0],
                char,
            ) for char in text
        )
        return self.__combiningDiacriticsRegEx.sub('', text)

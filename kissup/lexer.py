import re
from collections import namedtuple


TEXT_BACKSLASH_CHARS = {'[', ']', '\\'}
STRING_LITERAL_BACKSLASH_CHARS = {'"', '\\'}


class LexError(Exception):
    pass


TokenSpec = namedtuple('Token', ['match_re', 'get_token'])


class Token:
    def __init__(self, line_num, pos, value):
        super().__init__()
        self.line_num = line_num
        self.pos = pos
        self.value = value

    def __eq__(self, other):
        return (
            type(self) is type(other) and
            self.value == other.value and
            self.line_num == other.line_num and
            self.pos == other.pos)

    def __repr__(self):
        return "{}(line_num={}, pos={}, value={!r})".format(
            self.__class__.__name__, self.line_num, self.pos, self.value)


class BracketLeftToken(Token):
    name = "["
    def __init__(self, line_num, pos, value='['):
        super().__init__(line_num, pos, value)

class BracketRightToken(Token):
    name = "]"
    def __init__(self, line_num, pos, value=']'):
        super().__init__(line_num, pos, value)

class BBWordToken(Token):
    name = "bbword"

class EqualsToken(Token):
    name = "="
    def __init__(self, line_num, pos, value='='):
        super().__init__(line_num, pos, value)

class SlashToken(Token):
    name = "/"
    def __init__(self, line_num, pos, value='/'):
        super().__init__(line_num, pos, value)

class EndToken(Token):
    name = "ε"
    def __init__(self, line_num, pos, value=''):
        super().__init__(line_num, pos, value)

class TextToken(Token):
    name = "text"

class SpaceToken(Token):
    name = "space"


def _match_text(s, i, num_brackets, line, pos):
    """Match text"""

    if num_brackets > 0:
        return None

    chars = []

    while True:
        next_char = None
        is_last_char = len(s) <= i + 1
        if not is_last_char:
            next_char = s[i + 1]

        if i >= len(s) or s[i] == '[':
            if chars:
                return (TextToken(line, pos, ''.join(chars)), i, num_brackets)
            else:
                return None
        elif s[i] == ']':
            raise LexError("The character ']' must be escaped when used in text")
        elif s[i] == '\\':
            if next_char in TEXT_BACKSLASH_CHARS:
                chars.append(next_char)
                i += 1
            else:
                raise LexError(
                    "A backslash in text must be followed by one of: {}"
                        .format(TEXT_BACKSLASH_CHARS))
        else:
            chars.append(s[i])
            if is_last_char:
                return (TextToken(line, pos, ''.join(chars)), i + 1, num_brackets)
        i += 1


def _match_string_literal(s, i, num_brackets, line, pos):
    """Match string literal"""

    if num_brackets != 1:
        return None

    chars = []
    if s[i] != '"':
        return None
    i += 1

    while True:
        next_char = None
        is_last_char = len(s) > i + 1
        if not is_last_char:
            next_char = s[i]

        if s[i] == '"':
            return (TextToken(line, pos, ''.join(chars)), i + 1, num_brackets)
        elif s[i] == '\\':
            if next_char in STRING_LITERAL_BACKSLASH_CHARS:
                chars.append(next_char)
                i += 1
            else:
                raise LexError(
                    "A backslash in a string literal must be followed by one of: {}"
                        .format(STRING_LITERAL_BACKSLASH_CHARS))
        else:
            chars.append(s[i])
            if is_last_char:
                return (TextToken(line, pos, ''.join(chars)), i + 1, num_brackets)
        i += 1


def _match_left_bracket(s, i, num_brackets, line, pos):
    if num_brackets > 0:
        return None

    if s[i] == '[':
        return (BracketLeftToken(line, pos, s[i]), i + 1, num_brackets + 1)
    else:
        return None


def _match_right_bracket(s, i, num_brackets, line, pos):
    if num_brackets < 1:
        return None

    if s[i] == ']':
        return (BracketRightToken(line, pos, s[i]), i + 1, num_brackets - 1)
    else:
        return None


def _make_re_matcher(expr, required_num_brackets, Cls):
    re_compiled = re.compile(expr)
    def match(s, i, num_brackets, line, pos):
        match = re_compiled.match(s, i)
        if match and num_brackets == required_num_brackets:
            text = match.group(0)
            return (Cls(line, pos, text), i + len(text), num_brackets)
        else:
            return None
    match.__doc__ = """Match re {!r}""".format(expr)
    return match


TOKEN_FNS = [
    _match_left_bracket,
    _make_re_matcher(r'[^[\]\s=/]+', 1, BBWordToken),
    _make_re_matcher(r'\s+', 1, SpaceToken),
    _make_re_matcher(r'=', 1, EqualsToken),
    _match_string_literal,
    _make_re_matcher(r'/', 1, SlashToken),
    _match_right_bracket,
    _match_text,
]


def lex_kissup(s):
    line_indexes = [0] + [m.start() for m in re.findall('\n', s)] + [len(s)]
    line = 0
    i = 0
    num_brackets = 0
    while i < len(s):
        j = i
        while line_indexes[line] < - i:
            line += 1
        for token_fn in TOKEN_FNS:
            result = token_fn(s, i, num_brackets, line, i - line_indexes[line])
            if result:
                (token, i, num_brackets) = result
                yield token
                break
        if j == i:
            raise LexError("Could not match character {}".format(s[i]))

    while line_indexes[line] < - i:
        line += 1

    yield EndToken(line, i - line_indexes[line], '')

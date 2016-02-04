import re
from collections import namedtuple


TEXT_BACKSLASH_CHARS = {'[', ']', '\\'}
STRING_LITERAL_BACKSLASH_CHARS = {'"', '\\'}


class LexError(Exception):
    pass


TokenSpec = namedtuple('Token', ['match_re', 'get_token'])


class Token:
    def __init__(self, line_num, pos, value):
        super()
        self.line_num = line_num
        self.pos = pos
        self.value = value

    def __eq__(self, other):
        return (
            self.name == other.name and
            self.value == other.value and
            self.line_num == other.line_num and
            self.pos == other.pos)

    def __repr__(self):
        return "{}(line_num={}, pos={}, value={!r})".format(
            self.name, self.line_num, self.pos, self.value)


class BracketLeftToken(Token):
    name = "BRACKET_LEFT"
class BracketRightToken(Token):
    name = "BRACKET_RIGHT"
class BBWordToken(Token):
    name = "BBWORD"
class EqualsToken(Token):
    name = "EQUALS"
class EndToken(Token):
    name = "END"
class TextToken(Token):
    name = "TEXT"
class SpaceToken(Token):
    name = "SPACE"


def _match_text(s, i, line, pos):
    """Match text"""
    chars = []
    while True:
        next_char = None
        is_last_char = len(s) <= i + 1
        if not is_last_char:
            next_char = s[i]

        if s[i] == '[':
            if chars:
                return (TextToken(line, pos, ''.join(chars)), i)
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
                return (TextToken(line, pos, ''.join(chars)), i + 1)
        i += 1


def _match_string_literal(s, i, line, pos):
    """Match string literal"""
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
            return (TextToken(line, pos, ''.join(chars)), i + 1)
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
                return (TextToken(line, pos, ''.join(chars)), i + 1)
        i += 1


def _make_const_matcher(char, Cls):
    def match(s, i, line, pos):
        if s[i] == char:
            return (Cls(line, pos, s[i]), i + 1)
        else:
            return None
    match.__doc__ = """Match const {!r}""".format(char)
    return match


def _make_re_matcher(expr, Cls):
    re_compiled = re.compile(expr)
    def match(s, i, line, pos):
        match = re_compiled.match(s, i)
        if match:
            text = match.group(0)
            return (Cls(line, pos, text), i + len(text))
        else:
            return None
    match.__doc__ = """Match re {!r}""".format(expr)
    return match


TOKEN_FNS = [
    _make_const_matcher('[', BracketLeftToken),
    _make_re_matcher(r'[^[\]\s=]+', BBWordToken),
    _make_re_matcher(r'\s+', SpaceToken),
    _make_const_matcher('=', EqualsToken),
    _match_string_literal,
    _make_const_matcher(']', BracketRightToken),
    _match_text,
]


def lex_kissup(s):
    line_indexes = [0] + [m.start() for m in re.findall('\n', s)] + [len(s)]
    line = 0
    i = 0
    while i < len(s):
        j = i
        while line_indexes[line] < - i:
            line += 1
        for token_fn in TOKEN_FNS:
            result = token_fn(s, i, line, i - line_indexes[line])
            if result:
                (token, i) = result
                yield token
                break
        if j == i:
            raise LexError("Could not match character {}".format(s[i]))
    yield EndToken(line, 0, '')

import re

from . import tokens


TEXT_BACKSLASH_CHARS = {'[', ']', '\\'}
STRING_LITERAL_BACKSLASH_CHARS = {'"', '\\'}


class LexError(Exception):
    def __init__(self, line, pos, msg):
        super().__init__("Line {} col {}: {}".format(line, pos, msg))


"""
# Matching function signature:

fn(string, index, num_brackets, line, col) -> None or (token, index, num_brackets)
ARGS
    string: the string
    index: index of character to lex in the string
    num_brackets: current bracket nesting depth
    line: line number
    col: column number within the line
RETURN
    token: a token object (whatever you want really)
    index: index of the next character to lex
    num_brackets: bracket nesting depth (may be the same or different)
"""


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
                return (tokens.TextToken(line, pos, ''.join(chars)), i, num_brackets)
            else:
                return None
        elif s[i] == ']':
            raise LexError(line, pos, "The character ']' must be escaped when used in text")
        elif s[i] == '\\':
            if next_char in TEXT_BACKSLASH_CHARS:
                chars.append(next_char)
                i += 1
            else:
                raise LexError(line, pos,
                    "A backslash in text must be followed by one of: {}"
                        .format(TEXT_BACKSLASH_CHARS))
        else:
            chars.append(s[i])
            if is_last_char:
                return (tokens.TextToken(line, pos, ''.join(chars)), i + 1, num_brackets)
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
        if i >= len(s):
            return None
        elif s[i] == '"':
            return (tokens.StringToken(line, pos, ''.join(chars)), i + 1, num_brackets)
        elif s[i] == '\\':
            next_char = None
            try:
                next_char = s[i + 1]
            except IndexError:
                pass

            if next_char in STRING_LITERAL_BACKSLASH_CHARS:
                chars.append(next_char)
                i += 1
            else:
                raise LexError(line, pos,
                    "A backslash in a string literal must be followed by one of: {}"
                        .format(STRING_LITERAL_BACKSLASH_CHARS))
        else:
            chars.append(s[i])
        i += 1


def _match_left_bracket(s, i, num_brackets, line, pos):
    if num_brackets > 0:
        return None

    if s[i] == '[':
        return (tokens.BracketLeftToken(line, pos, s[i]), i + 1, num_brackets + 1)
    else:
        return None


def _match_right_bracket(s, i, num_brackets, line, pos):
    if num_brackets < 1:
        return None

    if s[i] == ']':
        return (tokens.BracketRightToken(line, pos, s[i]), i + 1, num_brackets - 1)
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
    _make_re_matcher(r'[^[\]\s=/"]+', 1, tokens.BBWordToken),
    _make_re_matcher(r'\s+', 1, tokens.SpaceToken),
    _make_re_matcher(r'=', 1, tokens.EqualsToken),
    _match_string_literal,
    _make_re_matcher(r'/', 1, tokens.SlashToken),
    _match_right_bracket,
    _match_text,
]


def lex_kissup(s):
    line_indexes = [0] + [m.start() for m in re.finditer('\n', s)] + [len(s)]
    line = 0
    i = 0
    num_brackets = 0
    while i < len(s):
        j = i
        while line_indexes[line] < - i:
            line += 1
        pos = i - line_indexes[line]
        for token_fn in TOKEN_FNS:
            result = token_fn(s, i, num_brackets, line, pos)
            if result:
                (token, i, num_brackets) = result
                yield token
                break
        if j == i:
            raise LexError(line, pos, "Could not match character {}".format(s[i]))

    while line_indexes[line] < - i:
        line += 1

    yield tokens.EndToken(line, i - line_indexes[line], '')

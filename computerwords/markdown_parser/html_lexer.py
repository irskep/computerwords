import re

from . import tokens
from .exceptions import SourceException
from .src_loc import SourceLocation


LEFT_ANGLE_BRACKET = '<'
RIGHT_ANGLE_BRACKET = '>'
TEXT_BACKSLASH_CHARS = {LEFT_ANGLE_BRACKET, RIGHT_ANGLE_BRACKET, '[', ']', '\\'}
STRING_LITERAL_BACKSLASH_CHARS = {'"', '\\'}


class LexError(SourceException): pass


"""
# Matching function signature:

```
fn(string, index, num_brackets, start_loc, get_loc_at)
    -> None or (token, index, num_brackets)
ARGS
    string: the string
    index: index of character to lex in the string
    num_brackets: current bracket nesting depth
    start_loc: SourceLocation corresponding to index
    get_loc_at(i): function that returns the location at string index i
RETURN
    token: a token object (whatever you want really)
    index: index of the next character to lex
    num_brackets: bracket nesting depth (may be the same or different)
```
"""


def _match_text(s, i, num_brackets, start_loc, get_loc_at):
    """Match text"""

    if num_brackets > 0:
        return None

    chars = []

    while True:
        next_char = None
        is_last_char = len(s) <= i + 1
        if not is_last_char:
            next_char = s[i + 1]

        if i >= len(s) or s[i] == LEFT_ANGLE_BRACKET:
            if chars:
                return (
                    tokens.TextToken(
                        start_loc.to(get_loc_at(i)),
                        ''.join(chars)),
                    i,
                    num_brackets)
            else:
                return None
        elif s[i] == RIGHT_ANGLE_BRACKET:
            raise LexError(
                get_loc_at(i).as_range,
                "The character '>' must be escaped when used in text")
        elif s[i] == '\\':
            if next_char in TEXT_BACKSLASH_CHARS:
                chars.append(next_char)
                i += 1
            else:
                raise LexError(
                    get_loc_at(i).as_range,
                    "A backslash in text must be followed by one of: {}"
                        .format(sorted(TEXT_BACKSLASH_CHARS)))
        else:
            chars.append(s[i])
            if is_last_char:
                return (
                    tokens.TextToken(
                        start_loc.to(get_loc_at(i + 1)),
                        ''.join(chars)),
                    i + 1,
                    num_brackets)
        i += 1


def _match_string_literal(s, i, num_brackets, start_loc, get_loc_at):
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
            return (
                tokens.StringToken(
                    start_loc.to(get_loc_at(i + 1)),
                    ''.join(chars)),
                i + 1,
                num_brackets)
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
                raise LexError(
                    get_loc_at(i).as_range,
                    "A backslash in a string literal must be followed by one of: {}"
                        .format(sorted(STRING_LITERAL_BACKSLASH_CHARS)))
        else:
            chars.append(s[i])
        i += 1


def _match_left_bracket(s, i, num_brackets, start_loc, get_loc_at):
    if num_brackets > 0:
        return None

    if s[i] == LEFT_ANGLE_BRACKET:
        return (
            tokens.BracketLeftToken(start_loc.to(get_loc_at(i + 1)), s[i]),
            i + 1,
            num_brackets + 1)
    else:
        return None


def _match_right_bracket(s, i, num_brackets, start_loc, get_loc_at):
    if num_brackets < 1:
        return None

    if s[i] == RIGHT_ANGLE_BRACKET:
        return (
            tokens.BracketRightToken(start_loc.to(get_loc_at(i + 1)), s[i]),
            i + 1,
            num_brackets - 1)
    else:
        return None


def _make_re_matcher(expr, required_num_brackets, Cls):
    re_compiled = re.compile(expr)
    def match(s, i, num_brackets, start_loc, get_loc_at):
        match = re_compiled.match(s, i)
        if match and num_brackets == required_num_brackets:
            text = match.group(0)
            return (
                Cls(start_loc.to(get_loc_at(i + len(text))), text),
                i + len(text),
                num_brackets)
        else:
            return None
    match.__doc__ = """Match re {!r}""".format(expr)
    return match


TOKEN_FNS = [
    _match_left_bracket,
    _make_re_matcher(r'[^[\<>\s=/"]+', 1, tokens.BBWordToken),
    _make_re_matcher(r'\s+', 1, tokens.SpaceToken),
    _make_re_matcher(r'=', 1, tokens.EqualsToken),
    _match_string_literal,
    _make_re_matcher(r'/', 1, tokens.SlashToken),
    _match_right_bracket,
    _match_text,
]


def lex_html_no_catch(s):
    line_indexes = [0] + [m.start() for m in re.finditer('\n', s)] + [len(s)]
    line = 0
    i = 0
    num_brackets = 0
    while i < len(s):
        j = i
        while line_indexes[line] < - i:
            line += 1
        col = i - line_indexes[line]
        loc = SourceLocation(line, col, i)

        def get_loc_at(i2):
            line2 = line
            while line_indexes[line2] < - i2:
                line2 += 1
            return SourceLocation(line, i2 - line_indexes[line2], i2)

        for token_fn in TOKEN_FNS:
            result = token_fn(s, i, num_brackets, loc, get_loc_at)
            if result:
                (token, i, num_brackets) = result
                yield token
                break
        if j == i:
            raise LexError(loc, "Could not match character {}".format(s[i]))

    while line_indexes[line] < - i:
        line += 1

    yield tokens.EndToken(
        SourceLocation(line, i - line_indexes[line], i).as_range, '')


def lex_html(config, s):
    try:
        return lex_html_no_catch(s)
    except SourceException as e:
        e.appy_config(config)
        raise e

import re
from collections import namedtuple


backslash_whitelist = {'[', ']'}


END = namedtuple('END')
BRACKET_LEFT = namedtuple('BRACKET_LEFT')
BRACKET_RIGHT = namedtuple('BRACKET_RIGHT')
TEXT = namedtuple('TEXT', ['value'])


class LexError(Exception):
    pass


class LexCursor:
    def __init__(self, chars):
        self.chars_iterator = chars_iterator
        self.char = None
        self.lookahead = chars.next()
        self.is_finished = false

    def advance(self, n=1):
        self._advance_one()

    def _advance_one(self):
        if self.is_finished:
            raise LexError("Lexer tried to advance when no characters remain")

        self.char = self.lookahead
        if self.char is None:
            self.is_finished = True

        try:
            self.lookahead = self.chars.next()
        except StopIteration:
            self.lookahead = None


def lex_kissup(chars):
    yield from _lex_kissup(LexCuror(chars))
    yield END()


def _lex_kissup(cursor):
    text_chars = []
    while not cursor.is_finished:
        if cursor.lookahead == '[':
            if len(text_chars):
                yield TEXT(value=''.join(text_chars))
            text_chars = []
            yield from _lex_code(cursor)
        elif cursor.char == ']':
            raise LexError("The character ']' must be escaped when used in text")
        elif cursor.char == "\\":
            if cursor.lookahead is None:
                raise LexError("Every backslash must be followed by the character to be escaped")
            elif cursor.lookahead not in backslash_whitelist:
                raise LexError("Only these characters may be escaped in text: {}".format(backslash_whitelist))
            else:
                cursor.advance()
            text_chars.append(cursor.char)
        else:
            text_chars.append(cursor.char)

        cursor.advance()


def _lex_code(cursor):
    word_chars = []
    while not cursor.is_finished:
        if cursor.lookahead == '[':
            if len(text_chars):
                yield TEXT(value=''.join(text_chars))
            text_chars = []
            yield from _lex_code(cursor)
        elif cursor.char == ']':
            raise LexError("The character ']' must be escaped when used in text")
        elif cursor.char == "\\":
            if cursor.lookahead is None:
                raise LexError("Every backslash must be followed by the character to be escaped")
            elif cursor.lookahead not in backslash_whitelist:
                raise LexError("Only these characters may be escaped in text: {}".format(backslash_whitelist))
            else:
                cursor.advance()
            text_chars.append(cursor.char)
        else:
            text_chars.append(cursor.char)

        cursor.advance()

from .src_loc import SourceRange


class Token:
    def __init__(self, loc, value):
        super().__init__()
        assert(isinstance(loc, SourceRange))
        self.value = value
        self.loc = loc

    def __eq__(self, other):
        return (
            type(self) is type(other) and
            self.value == other.value and
            self.loc == other.loc)

    def __repr__(self):
        return "{}(value={!r}, loc={!r})".format(
            self.__class__.__name__, self.value, self.loc)

    def __hash__(self):
        return hash(repr(self))


class BracketLeftToken(Token):
    name = "<"
    def __init__(self, loc, value='<'):
        super().__init__(loc, value)

class BracketRightToken(Token):
    name = ">"
    def __init__(self, loc, value='>'):
        super().__init__(loc, value)

class BBWordToken(Token):
    name = "BBWORD"

class EqualsToken(Token):
    name = "="
    def __init__(self, loc, value='='):
        super().__init__(loc, value)

class SlashToken(Token):
    name = "/"
    def __init__(self, loc, value='/'):
        super().__init__(loc, value)

class EndToken(Token):
    name = "ε"
    def __init__(self, loc, value=''):
        super().__init__(loc, value)

class TextToken(Token):
    name = "TEXT"

class StringToken(Token):
    name = "STRING"

class SpaceToken(Token):
    name = "SPACE"

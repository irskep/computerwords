class Token:
    def __init__(self, line, pos, value):
        super().__init__()
        self.line = line
        self.pos = pos
        self.value = value

    def __eq__(self, other):
        return (
            type(self) is type(other) and
            self.value == other.value and
            self.line == other.line and
            self.pos == other.pos)

    def __repr__(self):
        return "{}(line={}, pos={}, value={!r})".format(
            self.__class__.__name__, self.line, self.pos, self.value)

    def __hash__(self):
        return hash(repr(self))


class BracketLeftToken(Token):
    name = "<"
    def __init__(self, line, pos, value='<'):
        super().__init__(line, pos, value)

class BracketRightToken(Token):
    name = ">"
    def __init__(self, line, pos, value='>'):
        super().__init__(line, pos, value)

class BBWordToken(Token):
    name = "BBWORD"

class EqualsToken(Token):
    name = "="
    def __init__(self, line, pos, value='='):
        super().__init__(line, pos, value)

class SlashToken(Token):
    name = "/"
    def __init__(self, line, pos, value='/'):
        super().__init__(line, pos, value)

class EndToken(Token):
    name = "ε"
    def __init__(self, line, pos, value=''):
        super().__init__(line, pos, value)

class TextToken(Token):
    name = "TEXT"

class StringToken(Token):
    name = "STRING"

class SpaceToken(Token):
    name = "SPACE"

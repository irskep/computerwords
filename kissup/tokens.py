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
    name = "BBWORD"

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
    name = "TEXT"

class StringToken(Token):
    name = "STRING"

class SpaceToken(Token):
    name = "SPACE"

from collections import namedtuple


SourceLocationBase = namedtuple('SourceLocationBase', ['line', 'col', 'char'])
class SourceLocation(SourceLocationBase):

    def to(self, other):
        return SourceRange(self, other)

    def plus(self, n):
        return SourceRange(
            self, SourceLocation(self.line, self.col + n, self.char + n))

    def relative_to(self, other):
        """
        Return an absolute SourceLocation by adding this one to another one.
        "This one" is the relative location; the other is the base.
        """
        char = None if self.char is None or other.char is None else self.char + other.char
        if char is not None:
            assert(char >= 0)
        line = self.line + other.line
        if self.line == 0:
            return SourceLocation(line, self.col + other.col, char)
        else:
            return SourceLocation(line, self.col, char)

    @property
    def as_range(self):
        return self.to(self)

    @property
    def short_str(self):
        return "{}:{}".format(self.line + 1, self.col + 1)

    def __str__(self):
        return "Line {}, col {}".format(self.line + 1, self.col + 1)


SourceRangeBase = namedtuple('SourceRangeBase', ['start', 'end'])
class SourceRange(SourceRangeBase):

    def relative_to(self, other):
        return SourceRange(
            self.start.relative_to(other.start),
            self.end.relative_to(other.start))

    @property
    def short_str(self):
        fmt = ""

        if self.start == self.end:
            return self.start.short_str
        elif self.start.line == self.end.line:
            fmt = "{start_line}:{start_col}-{end_col}"
        else:
            fmt = "{start_line}:{start_col}-{end_line}:{end_col}"
        return fmt.format(
            start_line=self.start.line + 1,
            start_col=self.start.col + 1,
            end_line=self.end.line + 1,
            end_col=self.end.col + 1)

    def __str__(self):
        fmt = ""
        if self.start == self.end:
            return str(self.start)
        elif self.start.line == self.end.line:
            fmt = "Line {start_line}, col {start_col}-{end_col}"
        else:
            fmt = "Line {start_line}, col {start_col}-Line {end_line}, col {end_col}"
        return fmt.format(
            start_line=self.start.line + 1,
            start_col=self.start.col + 1,
            end_line=self.end.line + 1,
            end_col=self.end.col + 1)

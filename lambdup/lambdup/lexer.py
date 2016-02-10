#!/usr/bin/env python2

import functools


class Token(object):

    def __init__(self, token, lexeme, pos):
        self.token = token
        self.lexeme = lexeme
        self.pos = pos


@functools.total_ordering
class SourceLocation(object):

    def __init__(self, path, start_line, start_col, end_line, end_col):
        self.path = path
        self.start_line = start_line
        self.start_col = start_col
        self.end_line = end_line
        self.end_col = end_col

    def tuple(self):
        return (self.path, self.start_line, self.start_col, self.end_line, self.end_col)

    def __eq__(a, b):
        return a.tuple() == b.tuple()

    def __lt__(a, b):
        return a.tuple() < b.tuple()

    def _order(a, b):
        if b < a:
            return b, a
        return a, b

    def adjacent(self, other):
        if self.path != other.path:
            return False
        a, b = self._order(other)
        if a.end_line != b.start_line:
            return False
        if a.end_col + 1 == b.start_col:
            return True
        return False

    def merge(self, other):
        if not self.adjacent(other):
            raise Exception, "cannot merge non-adjacent locations"
        a, b = self._order(other)
        return SourceLocation(
            a.path, a.start_line, a.start_col, b.end_line, b.end_col)

    def __repr__(self): return str(self)

    def __str__(self):
        return '<SourceLocation %s (%d:%d)-(%d:%d)>' % self.tuple()


class LocationRange(object):

    def __init__(self, *locations):
        if len(locations) <= 0:
            raise Exception, "must have at least 1 location in range"
        locations.sort()
        merged = [locations[0]]
        for loc in locations[1:]:
            if merged[-1].adjacent(loc):
                merged[-1] = merged[-1].merge(loc)
        self.locations = merged

    def __repr__(self): return str(self)

    def __str__(self):
        return '<LocationRange %s>' % str(self.locations)


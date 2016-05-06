import json
from collections import namedtuple


SymbolDefBase = namedtuple(
    'SymbolDef',
    ['id', 'parent_id', 'type', 'name', 'docstring',
     'string_inside_parens', 'return_value', 'source_file_path', 'line_number',
     'relative_path', 'children'])


class SymbolDef(SymbolDefBase):
    """Represents a single line of a symbol file."""
    def __hash__(self):
        return hash(self.id)


class SymbolTree:
    """
    Tree-structured representation of a symbol file.
    """

    def __init__(self, json_string_lines):
        self.root = _create_symbol_tree(
            [json.loads(line) for line in json_string_lines])

    def lookup(self, path):
        """Returns the symbol at *path* or raises `KeyError`."""
        parts = path.split('.')
        assert(parts[0] == self.root.name)
        if len(parts) == 1:
            return self.root
        try:
            return _get_symbol_at_path(self.root, parts[1:])
        except KeyError as e:
            raise KeyError("Symbol not found: {}".format(path))

    def debug_print(self, t=None, i=0):
        t = t or self.root
        print("{}SymbolDef({}, {}, {})".format(" " * i, t.id, t.type, t.name))
        for child in t.children:
            self.debug_print(child, i + 2)


def _create_symbol_tree(symbol_defs):
    nodes_by_id = {}
    for symbol in symbol_defs:
        nodes_by_id[symbol['id']] = SymbolDef(children=[], **symbol)

    roots = []
    for symbol in nodes_by_id.values():
        if symbol.parent_id:
            nodes_by_id[symbol.parent_id].children.append(symbol)
        else:
            roots.append(symbol)
    assert(len(roots) == 1)
    return roots[0]


def _get_symbol_at_path(t, parts):
    matching_children = [s for s in t.children if s.name == parts[0]]
    if not matching_children:
        raise KeyError(parts[0])
    next_symbol = matching_children[0]
    if len(parts) == 1:
        return next_symbol
    else:
        return _get_symbol_at_path(next_symbol, parts[1:])

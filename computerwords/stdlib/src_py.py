import json
import pathlib
from collections import namedtuple

from computerwords.cwdom.nodes import CWTagNode, CWTextNode
from computerwords.cwdom.traversal import find_ancestor
from computerwords.markdown_parser.cfm_to_cwdom import cfm_to_cwdom


SymbolDef = namedtuple(
    'SymbolDef', ['id', 'parent_id', 'type', 'name', 'docstring', 'children'])


def read_config(config):
    symbols_path = pathlib.Path(config['python']['symbols_path'])
    config['python']['resolved_symbols_path'] = (
        config['root_dir'].joinpath(symbols_path))


def _create_symbol_tree(symbol_defs):
    # {"parent": 1, "docstring": null, "id": 2, "name": "__main__", "type": "module"}
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


def _debug_print_tree(t, i=0):
    print("{}SymbolDef({}, {}, {})".format(" " * i, t.id, t.type, t.name))
    for child in t.children:
        _debug_print_tree(child, i + 2)


def _get_symbol_at_path(t, parts):
    next_symbol = [s for s in t.children if s.name == parts[0]][0]
    if len(parts) == 1:
        return next_symbol
    else:
        return _get_symbol_at_path(next_symbol, parts[1:])



def get_symbol_at_path(root, path):
    parts = path.split('.')
    assert(parts[0] == root.name)
    return _get_symbol_at_path(root, parts[1:])


def _get_symbol_node(library, path, symbol, h_level=2, full_path=True):
    prefix = {
        'class': 'class ',
        'function': 'function ',
    }.get(symbol.type, '')
    text = path if full_path else symbol.name
    suffix = '()' if symbol.type in {'class', 'function', 'method'} else ''
    tag_node = CWTagNode('h{}'.format(h_level), {}, [
        CWTagNode('tt', {}, [CWTextNode(prefix + text + suffix)])
    ])
    tag_node.data['ref_id_override'] = path
    children = [tag_node]
    if symbol.docstring:
        children.append(CWTagNode(
            'div', {'class': 'autodoc-docstring-body'},
            children=cfm_to_cwdom(symbol.docstring, library.get_allowed_tags())))
    return CWTagNode(
        'div', kwargs={'class': 'autodoc-{}'.format(symbol.type)},
        children=children)


def _get_symbol_nodes_recursive(library, parent_path, symbol, h_level):
    if symbol.name.startswith('_'):
        return
    path = parent_path + '.' + symbol.name
    yield _get_symbol_node(library, path, symbol, h_level, full_path=False)
    for child in symbol.children:
        yield from _get_symbol_nodes_recursive(library, path, child, h_level + 1)


def add_src_py(library):
    @library.processor('autodoc-python')
    def process_autodoc_module(tree, node):
        if 'autodoc_symbols' not in tree.processor_data:
            config = tree.env['config']
            with config['python']['resolved_symbols_path'].open() as f:
                symbol_defs = [json.loads(line) for line in f]
                tree.processor_data['autodoc_symbols'] = symbol_defs
                symbol_tree = _create_symbol_tree(symbol_defs)
                tree.processor_data['autodoc_symbol_tree'] = symbol_tree

        symbol_tree = tree.processor_data['autodoc_symbol_tree']

        symbol = None
        symbol_node = None
        symbol_path = None
        if 'module' in node.kwargs:
            symbol_path = node.kwargs['module']
        else:
            return

        symbol = get_symbol_at_path(symbol_tree, symbol_path)
        symbol_node = _get_symbol_node(library, symbol_path, symbol, h_level=2)
        tree.replace_subtree(node, symbol_node)

        if (    node.kwargs.get('include-children', 'false').lower() == 'true'
                and symbol.children):
            new_siblings = []
            for child in symbol.children:
                new_siblings += list(_get_symbol_nodes_recursive(
                    library, symbol_path, child, h_level=3))
            tree.add_siblings_ahead(new_siblings)

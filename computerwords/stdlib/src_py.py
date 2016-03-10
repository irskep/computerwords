import json
import pathlib
from collections import namedtuple

from computerwords.cwdom.nodes import CWTagNode, CWTextNode
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

        if 'module' in node.kwargs:
            symbol = get_symbol_at_path(symbol_tree, node.kwargs['module'])
            children = [
                CWTagNode('h1', {}, [
                    CWTagNode('tt', {}, [
                        CWTextNode(node.kwargs['module'])
                    ])
                ])
            ]
            if symbol.docstring:
                children += cfm_to_cwdom(symbol.docstring, library.get_allowed_tags())
            tree.replace_subtree(node, CWTagNode(
                'div', kwargs={'class': 'autodoc-module'}, children=children))
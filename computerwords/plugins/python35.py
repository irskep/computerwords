import pathlib

from computerwords.plugin import CWPlugin

from computerwords.cwdom.nodes import CWTagNode, CWTextNode
from computerwords.cwdom.traversal import find_ancestor
from computerwords.markdown_parser import CFMParserConfig
from computerwords.markdown_parser.cfm_to_cwdom import cfm_to_cwdom
from computerwords.symbol_tree import SymbolTree


class AutodocPythonException(Exception): pass


class Python35Plugin(CWPlugin):

    CONFIG_NAMESPACE = "python3.5"

    def get_default_config(self):
        return {
            "symbols_path": "symbols.json",
        }

    def postprocess_config(self, config):
        symbols_path = pathlib.Path(config['python3.5']['symbols_path'])
        config['python3.5']['resolved_symbols_path'] = (
            config['root_dir'].joinpath(symbols_path))

    def add_processors(self, library):
        self.library = library
        library.processor('autodoc-python', self.process_autodoc_module)

    def process_autodoc_module(self, tree, node):
        # load symbol tree
        if 'autodoc_symbol_tree' not in tree.processor_data:
            config = tree.env['config']
            with config['python3.5']['resolved_symbols_path'].open() as f:
                tree.processor_data['autodoc_symbol_tree'] = SymbolTree(f)

        symbol_tree = tree.processor_data['autodoc_symbol_tree']

        output_dir = tree.env['output_dir'] / 'src'
        output_url = tree.env['config']['html']['site_url'] + "src/"

        # figure out what we're showing

        symbol_path, h_level = _get_symbol_path_and_h_level(node)

        render_absolute_path = (
            node.kwargs.get('render-absolute-path', 'true').lower() == 'true')

        # prepare to parse. in the future, we should probably shell out to
        # computerwords or something rather than assuming the same config.

        parser_config = CFMParserConfig(
            document_id=(symbol_path,),
            document_path=symbol_path,
            allowed_tags=self.library.get_allowed_tags())

        # replace cursor with symbol contents

        try:
            symbol = symbol_tree.lookup(symbol_path)
        except KeyError as e:
            raise AutodocPythonException(
                "Symbol not found: {}".format(symbol_path))

        all_symbols = {symbol}
        symbol_node = _get_symbol_node(
            parser_config, output_url, symbol_path, symbol, h_level=h_level,
            full_path=render_absolute_path)
        tree.replace_subtree(node, symbol_node)

        # optionally, add children ahead of cursor (avoid creating deeply
        # nested markup)

        if (    node.kwargs.get('include-children', 'false').lower() == 'true'
                and symbol.children):
            new_siblings = []
            for child in symbol.children:
                new_siblings += list(_get_symbol_nodes_recursive(
                    parser_config, output_url, symbol_path, child, h_level + 1,
                    all_symbols))
            tree.add_siblings_ahead(new_siblings)

        # write source files (hacky, will fix)

        src_paths = set(
            (symbol.source_file_path, symbol.relative_path)
            for symbol in all_symbols)

        for src, rel_dest in src_paths:
            abs_dest = output_dir / (rel_dest + ".html")
            abs_dest.parent.mkdir(parents=True, exist_ok=True)
            with open(src, 'r') as src_f:
                with abs_dest.open('w') as dest_f:
                    _write_linkable_src(src_f, dest_f, rel_dest)


def _get_symbol_path_and_h_level(node):
    symbol_path = None
    h_level = 2
    if 'module' in node.kwargs:
        symbol_path = node.kwargs['module']
        h_level = int(node.kwargs.get('heading-level', "1"))
    elif 'class' in node.kwargs:
        symbol_path = node.kwargs['class']
        h_level = int(node.kwargs.get('heading-level', "2"))
    elif 'method' in node.kwargs:
        symbol_path = node.kwargs['method']
        h_level = int(node.kwargs.get('heading-level', "3"))
    elif 'function' in node.kwargs:
        symbol_path = node.kwargs['function']
        h_level = int(node.kwargs.get('heading-level', "2"))
    else:
        raise AutodocPythonException(
            "No content specified (module|class|method|function)")
    return symbol_path, h_level


def _get_symbol_nodes_recursive(parser_config, output_url, parent_path, symbol, h_level, all_symbols):
    if symbol.name.startswith('_') and symbol.name != '__init__':
        return
    if not symbol.docstring:
        return
    path = parent_path + '.' + symbol.name
    all_symbols.add(symbol)
    yield _get_symbol_node(parser_config, output_url, path, symbol, h_level, full_path=False)
    for child in symbol.children:
        yield from _get_symbol_nodes_recursive(
            parser_config, output_url, path, child, h_level + 1, all_symbols)


def _get_symbol_node(parser_config, output_url, path, symbol, h_level=2, full_path=True):
    output_path = output_url + symbol.relative_path + ".html"
    if symbol.line_number:
        output_path += '#{}'.format(symbol.line_number)

    name_nodes = []

    if symbol.type in {'class', 'function'}:
        name_nodes.append(
            CWTagNode('span', {'class': 'autodoc-keyword'}, [
                CWTextNode(symbol.type + ' ')
            ]))

    name_nodes.append(
        CWTagNode('span', {'class': 'autodoc-identifier'}, [
            CWTextNode(path if full_path else symbol.name)
        ]))

    if symbol.string_inside_parens is not None:
        name_nodes.append(
            CWTagNode('span', {'class': 'autodoc-arguments'}, [
                CWTextNode('(' + symbol.string_inside_parens + ')')
            ]))

    if symbol.return_value:
        name_nodes.append(
            CWTagNode('span', {'class': 'autodoc-return-value'}, [
                CWTextNode(' &rarr; ', escape=False),
                CWTextNode(symbol.return_value)
            ]))

    heading_node = CWTagNode('h{}'.format(h_level), {}, [
        CWTagNode('code', {}, name_nodes),
        CWTagNode('a', {'href': output_path, 'class': 'autodoc-source-link'}, [
            CWTextNode('src')
        ])
    ])
    heading_node.data['ref_id_override'] = path

    children = [heading_node]

    if symbol.docstring:
        css_class = 'autodoc-{}-docstring-body'.format(symbol.type)
        docstring_children = cfm_to_cwdom(symbol.docstring, parser_config)
        children.append(CWTagNode(
            'div', {'class': css_class}, children=docstring_children))
    node = CWTagNode(
        'section', kwargs={'class': 'autodoc-{}'.format(symbol.type)},
        children=children)
    return node



def _write_linkable_src(src_f, dest_f, name):
    """Pretty hacky for now but it works"""

    dest_f.write("""<!doctype html>
<html>
    <head>
        <title>{name}</title>""".format(name=name))
    dest_f.write("""
        <style>
            pre {
                margin: 0;
                line-height: 120%;
            }
            a {
                display: block;
            }
            a:target {
                background-color: #cdf;
            }
        </style>
    </head>
    <body class="autodoc-source">
""")

    for i, line in enumerate(src_f):
        dest_f.write("""
<a name={i}><pre>{line}</pre></a>
        """.format(i=i + 1, line=line.rstrip() or '&nbsp;'))

    dest_f.write("""
    </body>
</html>""")


__all__ = ['Python35Plugin']

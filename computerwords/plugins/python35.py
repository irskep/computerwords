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
            "source_code_url_format": None,
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
        src_url_fmt = tree.env['config']['python3.5']['source_code_url_format']

        # figure out what we're showing

        symbol_path, h_level = _get_symbol_path_and_h_level(node)

        should_render_absolute_path = (
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
                "Symbol not found: {} (somewhere in {})".format(
                    symbol_path, tree.get_document_path(node.document_id)))

        all_symbols = {symbol}
        symbol_node = _get_symbol_node(
            parser_config, src_url_fmt, symbol_path, symbol,
            h_level=h_level, full_path=should_render_absolute_path)
        tree.replace_subtree(node, symbol_node)

        # optionally, add children ahead of cursor (avoid creating deeply
        # nested markup)

        if (    node.kwargs.get('include-children', 'false').lower() == 'true'
                and symbol.children):
            new_siblings = []
            for child in symbol.children:
                new_siblings += list(_get_symbol_nodes_recursive(
                    parser_config, src_url_fmt, symbol_path, child,
                    h_level + 1, all_symbols))
            tree.add_siblings_ahead(new_siblings)


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


def _get_symbol_nodes_recursive(
        parser_config, src_url_fmt, parent_path, symbol, h_level, all_symbols):
    if symbol.name.startswith('_') and symbol.name != '__init__':
        return
    if not symbol.docstring:
        return
    path = parent_path + '.' + symbol.name
    all_symbols.add(symbol)
    yield _get_symbol_node(
        parser_config, src_url_fmt, path, symbol, h_level, full_path=False)
    for child in symbol.children:
        yield from _get_symbol_nodes_recursive(
            parser_config, src_url_fmt, path, child, h_level + 1, all_symbols)


def _get_symbol_node(
        parser_config, src_url_fmt, path, symbol, h_level=2, full_path=True):
    src_link_nodes = []

    if src_url_fmt:
        output_url = src_url_fmt.format(
            relative_path=symbol.relative_path,
            line_number=symbol.line_number)
        link =  CWTagNode(
            'a', {'href': output_url, 'class': 'autodoc-source-link'},
            [CWTextNode('src')])
        src_link_nodes = [link]

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

    heading_node = CWTagNode(
        'h{}'.format(h_level), {},
        [CWTagNode('code', {}, name_nodes)] + src_link_nodes
    )
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


__all__ = ['Python35Plugin']

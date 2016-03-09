import hashlib
import subprocess

import pygments
from pygments.formatters import HtmlFormatter
from pygments.lexers import get_lexer_by_name
from pygments.util import ClassNotFound

from computerwords.cwdom.nodes import CWTagNode, CWTextNode


def _dumb_parse_args(s):
    d = {}
    for pair in s.split():
        kv = pair.split('=', maxsplit=1)
        if len(kv) == 2:
            k, v = kv
            d[k] = v
    return d


def add_code(library):
    @library.processor('pre')
    def lang_pygments_convert(tree, node):
        try:
            split = (node.kwargs.get('language', '') or '').split(maxsplit=1)
            language = split[0] if split else None
            lexer = get_lexer_by_name(language)

            args = split[1] if len(split) > 1 else ''
            kwargs = _dumb_parse_args(args)

            figure_children = []

            if kwargs.get('filename', None):
                figure_children.append(
                    CWTagNode('div', {'class': 'filename'}, [
                        CWTextNode(kwargs['filename'])
                    ]))

            figure_children.append(CWTextNode(
                pygments.highlight(
                    node.children[0].text, lexer, HtmlFormatter()),
                escape=False))

            tree.replace_subtree(
                node,
                CWTagNode('figure', {'class': 'code'}, figure_children))
        except ClassNotFound:
            pass


    @library.processor('pre')
    def lang_graphviz_convert(tree, node):
        if node.kwargs.get('language', None) != 'graphviz-dot-convert':
            return

        code = node.children[0].text.encode('UTF-8')
        h = hashlib.sha256()
        h.update(code)

        # output_path = tree.env['output_dir'] / "{}.png".format(h.hexdigest())
        output_path = tree.env['output_dir'] / "{}.svg".format(h.hexdigest())
        src = output_path.relative_to(tree.env['output_dir'])
        # p = subprocess.Popen(
        #     ['dot', '-Tpng', '-Gdpi=192', '-o', str(output_path)], stdin=subprocess.PIPE)
        p = subprocess.Popen(
            ['dot', '-Tsvg', '-o', str(output_path)], stdin=subprocess.PIPE)
        p.communicate(code, timeout=10)
        tree.replace_subtree(
            node, CWTagNode('figure', {'class': 'image graphviz-graph'}, [
                CWTagNode('img', {'src': str(src)}),
            ]))

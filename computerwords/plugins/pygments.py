import pygments
from pygments.formatters import HtmlFormatter
from pygments.lexers import get_lexer_by_name
from pygments.util import ClassNotFound

from computerwords.plugin import CWPlugin

from computerwords.cwdom.nodes import CWTagNode, CWTextNode


class PygmentsPlugin(CWPlugin):

    CONFIG_NAMESPACE = 'pygments'

    def get_default_config(self):
        return {}

    def add_processors(self, library):
        @library.processor('pre')
        def lang_pygments_convert(tree, node):
            try:
                split = (
                    (node.kwargs.get('language', '') or '').split(maxsplit=1))
                language = split[0] if split else None
                lexer = get_lexer_by_name(language)

                args = split[1] if len(split) > 1 else ''
                kwargs = _dumb_parse_args(args)

                figure_children = []

                if kwargs.get('filename', None):
                    figure_children.append(
                        CWTagNode('figcaption', {'class': 'filename'}, [
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



def _dumb_parse_args(s):
    d = {}
    for pair in s.split():
        kv = pair.split('=', maxsplit=1)
        if len(kv) == 2:
            k, v = kv
            d[k] = v
    return d

__all__ = ['PygmentsPlugin']
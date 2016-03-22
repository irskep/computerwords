import logging

from computerwords.plugin import CWPlugin

from computerwords.cwdom.nodes import CWTagNode


log = logging.getLogger(__name__)


class CalloutsPlugin(CWPlugin):

    def add_processors(self, library):
        @library.processor('note')
        def lang_pygments_convert(tree, node):
            css_class = 'callout note'
            if node.kwargs.get('no-prefix', "false").lower() != "true":
                css_class += ' callout-auto-prefix'
            tree.replace_node(node, CWTagNode('div', {'class': css_class}))

        @library.processor('warning')
        def lang_pygments_convert(tree, node):
            css_class = 'callout warning'
            if node.kwargs.get('no-prefix', "false").lower() != "true":
                css_class += ' callout-auto-prefix'
            tree.replace_node(node, CWTagNode('div', {'class': css_class}))


__all__ = ['CalloutsPlugin']

import logging

from computerwords.plugin import CWPlugin

from computerwords.cwdom.nodes import CWTagNode


log = logging.getLogger(__name__)


class NotesPlugin(CWPlugin):

    def add_processors(self, library):
        @library.processor('note')
        def lang_pygments_convert(tree, node):
            css_class = 'note-note'
            if node.kwargs.get('no-prefix', "false").lower() != "true":
                css_class += ' note-auto-prefix'
            tree.replace_node(node, CWTagNode('aside', {'class': css_class}))

        @library.processor('warning')
        def lang_pygments_convert(tree, node):
            css_class = 'note-warning'
            if node.kwargs.get('no-prefix', "false").lower() != "true":
                css_class += ' note-auto-prefix'
            tree.replace_node(node, CWTagNode('aside', {'class': css_class}))


__all__ = ['NotesPlugin']

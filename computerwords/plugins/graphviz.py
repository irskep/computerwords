import hashlib
import subprocess

from computerwords.cwdom.nodes import CWTagNode, CWTextNode
from computerwords.plugin import CWPlugin


class GraphvizPlugin(CWPlugin):

    CONFIG_NAMESPACE = 'graphviz'

    def get_default_config(self):
        return {
            'format': 'svg',
        }

    def add_processors(self, library):
        @library.processor('pre')
        def lang_graphviz_convert(tree, node):
            if node.kwargs.get('language', None) != 'graphviz-dot-convert':
                return
            _do_graphviz(tree, node, node.children[0].text)


        @library.processor('pre')
        def lang_graphviz_convert(tree, node):
            if node.kwargs.get('language', None) != 'graphviz-simple':
                return
            _do_graphviz(tree, node, """
                strict digraph {
                    rankdir="LR";
                    node [fontname="Helvetica" fontsize=10 shape="box"];
                   """ + node.children[0].text + """
                }
            """)


def _do_graphviz(tree, node, text):
    output_format = tree.env['config']['graphviz']['format']

    code = text.encode('UTF-8')
    h = hashlib.sha256()
    h.update(code)

    filename = "{}.{}".format(h.hexdigest(), output_format)
    output_path = tree.env['output_dir'] / filename
    src = output_path.relative_to(tree.env['output_dir'])
    p = subprocess.Popen(
        ['dot', '-T' + output_format, '-o', str(output_path)],
        stdin=subprocess.PIPE)
    p.communicate(code, timeout=10)
    tree.replace_subtree(
        node, CWTagNode('figure', {'class': 'image graphviz-graph'}, [
            CWTagNode('img', {'src': str(src)}),
        ]))


__all__ = ['GraphvizPlugin']
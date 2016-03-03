import hashlib
import subprocess
from computerwords.cwdom.CWDOMNode import CWDOMTagNode


def add_code(library):

    @library.processor('pre')
    def lang_graphviz_convert(node_store, node):
        if node.kwargs.get('language', None) != 'graphviz-dot-convert':
            return

        code = node.children[0].text.encode('UTF-8')
        h = hashlib.sha256()
        h.update(code)

        output_path = node_store.env['output_dir'] / "{}.png".format(h.hexdigest())
        src = output_path.relative_to(node_store.env['output_dir'])
        p = subprocess.Popen(
            ['dot', '-Tpng', '-o', str(output_path)], stdin=subprocess.PIPE)
        p.communicate(code, timeout=10)
        node_store.replace_subtree(
            node, CWDOMTagNode('figure', {'class': 'image graphviz-graph'}, [
                CWDOMTagNode('img', {'src': str(src)}),
            ]))

import hashlib
import subprocess

from computerwords.cwdom.nodes import CWTagNode, CWTextNode


def _do_graphviz(tree, node, text):
    code = text.encode('UTF-8')
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


def add_graphviz(library):
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

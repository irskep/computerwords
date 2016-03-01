import subprocess
from computerwords.cwdom.CWDOMNode import CWDOMTagNode


LANGUAGES = {}
def language(l):
    def decorator(f):
        LANGUAGES[l] = f
    return decorator


diagram_num = 0
@language('graphviz-dot-convert')
def lang_graphviz_convert(node_store, node):
    global diagram_num
    diagram_num += 1
    output_path = node_store.env['output_dir'] / "{}.png".format(diagram_num)
    src = output_path.relative_to(node_store.env['output_dir'])
    p = subprocess.Popen(
        ['dot', '-Tpng', '-o', str(output_path)], stdin=subprocess.PIPE)
    p.communicate(node.children[0].text.encode('UTF-8'), timeout=10)
    node_store.replace_subtree(
        node.children[0], CWDOMTagNode('img', {'src': str(src)}))
    node_store.replace_node(
        node, CWDOMTagNode('div', {'class': 'graphviz-graph'}))


def add_code(library):
    @library.processor('pre')
    def process_anchor(node_store, node):
        language = node.kwargs.get('language', None)
        if language in LANGUAGES:
            LANGUAGES[language](node_store, node)

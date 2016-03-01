import hashlib
import subprocess
from computerwords.cwdom.CWDOMNode import CWDOMTagNode


LANGUAGES = {}
def language(l):
    def decorator(f):
        LANGUAGES[l] = f
    return decorator


@language('graphviz-dot-convert')
def lang_graphviz_convert(node_store, node):
    code = node.children[0].text.encode('UTF-8')
    h = hashlib.sha256()
    h.update(code)

    output_path = node_store.env['output_dir'] / "{}.png".format(h.hexdigest())
    src = output_path.relative_to(node_store.env['output_dir'])
    p = subprocess.Popen(
        ['dot', '-Tpng', '-o', str(output_path)], stdin=subprocess.PIPE)
    p.communicate(code, timeout=10)
    node_store.replace_subtree(
        node, CWDOMTagNode('div', {'class': 'graphviz-graph'}, [
            CWDOMTagNode('img', {'src': str(src)}),
        ]))


def add_code(library):
    @library.processor('pre')
    def process_anchor(node_store, node):
        language = node.kwargs.get('language', None)
        if language in LANGUAGES:
            LANGUAGES[language](node_store, node)

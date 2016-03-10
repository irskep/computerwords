import json
import pathlib

from computerwords.cwdom.nodes import CWTagNode, CWTextNode


def read_config(config):
    symbols_path = pathlib.Path(config['python']['symbols_path'])
    config['python']['resolved_symbols_path'] = (
        config['root_dir'].joinpath(symbols_path))


def add_src_py(library):
    @library.processor('autodoc-python')
    def process_autodoc_module(tree, node):
        if 'autodoc_symbols' not in tree.processor_data:
            config = tree.env['config']
            with config['python']['resolved_symbols_path'].open() as f:
                tree.processor_data['autodoc_symbols'] = [
                    json.loads(line) for line in f]
            print(tree.processor_data['autodoc_symbols'])
        tree.replace_subtree(node, CWTextNode("YOU DID A THING"))
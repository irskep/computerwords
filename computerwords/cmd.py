import argparse
import json
import logging
import pathlib
import sys

logging.basicConfig(level=logging.DEBUG)

from computerwords.htmlwriter import write as write_html
from computerwords.config import DictCascade, DEFAULT_CONFIG
from computerwords.cwdom.nodes import CWRootNode
from computerwords.cwdom.CWTree import CWTree
from computerwords.markdown_parser.cfm_to_cwdom import cfm_to_cwdom
from computerwords.read_doc_tree import read_doc_tree
from computerwords.stdlib import stdlib
from computerwords.stdlib.src_py import read_config

log = logging.getLogger(__name__)


def run():
    p = argparse.ArgumentParser()
    p.add_argument('--conf', default="conf.json", type=argparse.FileType('r'))
    p.add_argument('--debug', default=False, action='store_true')
    args = p.parse_args()

    config = dict(DictCascade(DEFAULT_CONFIG, json.load(args.conf)))
    files_root = pathlib.Path(args.conf.name).parent.resolve()
    config['root_dir'] = files_root
    output_root = pathlib.Path(files_root) / pathlib.Path(config['output_dir'])
    output_root.mkdir(exist_ok=True)

    read_config(config)

    def _get_doc_cwdom(subtree):
        with subtree.root_path.open() as f:
            return cfm_to_cwdom(f.read(), stdlib.get_allowed_tags())

    doc_tree, document_nodes = read_doc_tree(
        files_root, config['file_hierarchy'], _get_doc_cwdom)
    tree = CWTree(CWRootNode(document_nodes), {
        'doc_tree': doc_tree,
        'output_dir': output_root,
        'config': config
    })
    if args.debug:
        print(tree.root.get_string_for_test_comparison())
    tree.apply_library(stdlib)


    write_html(config, files_root, output_root, stdlib, tree)

import argparse
import json
import pathlib
import sys

from computerwords import htmlwriter
from computerwords.config import DictCascade, DEFAULT_CONFIG
from computerwords.cwdom.CWDOMNode import CWDOMRootNode
from computerwords.cwdom.NodeStore import NodeStore
from computerwords.markdown_parser.cfm_to_cwdom import (
    cfm_to_cwdom,
)
from computerwords.read_doc_tree import read_doc_tree
from computerwords.stdlib import stdlib


def run():
    p = argparse.ArgumentParser()
    p.add_argument('--conf', default="conf.json", type=argparse.FileType('r'))
    p.add_argument('--debug', default=False, action='store_true')
    args = p.parse_args()

    conf = DictCascade(DEFAULT_CONFIG, json.load(args.conf))
    files_root = pathlib.Path(args.conf.name).parent.resolve()
    output_root = pathlib.Path(files_root) / pathlib.Path(conf['output_dir'])
    output_root.mkdir(exist_ok=True)

    def _get_doc_cwdom(subtree):
        with subtree.root_path.open() as f:
            return cfm_to_cwdom(f.read(), stdlib.get_allowed_tags())
            # return string_to_cwdom(f.read(), stdlib.get_allowed_tags())

    doc_tree, document_nodes = read_doc_tree(
        files_root, conf['file_hierarchy'], _get_doc_cwdom)
    node_store = NodeStore(CWDOMRootNode(document_nodes), {
        'doc_tree': doc_tree,
        'output_dir': output_root,
    })
    if args.debug:
        print(node_store.root.get_string_for_test_comparison())
    node_store.apply_library(stdlib)


    htmlwriter.write(conf, files_root, output_root, stdlib, node_store)

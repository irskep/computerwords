import argparse
import json
import pathlib
import sys

from computerwords.markdown_parser.commonmark_to_cwdom import (
    commonmark_to_cwdom,
)
from computerwords.config import DictCascade, DEFAULT_CONFIG
from computerwords.cwdom.CWDOMNode import CWDOMRootNode
from computerwords.cwdom.NodeStore import NodeStore
from computerwords.htmlwriter import cwdom_to_html_string
from computerwords.read_doc_tree import read_doc_tree
from computerwords.stdlib import stdlib


def _get_doc_cwdom(subtree):
    with subtree.root_path.open() as f:
        return commonmark_to_cwdom(f.read())
        # return string_to_cwdom(f.read(), stdlib.get_allowed_tags())


def run():
    p = argparse.ArgumentParser()
    p.add_argument('--conf', default="conf.json", type=argparse.FileType('r'))
    p.add_argument('--debug', default=False, type=bool)
    args = p.parse_args()

    conf = DictCascade(DEFAULT_CONFIG, json.load(args.conf))
    files_root = pathlib.Path(args.conf.name).parent.resolve()

    doc_tree, document_nodes = read_doc_tree(
        files_root, conf['file_hierarchy'], _get_doc_cwdom)
    node_store = NodeStore(CWDOMRootNode(document_nodes), {
        'doc_tree': doc_tree
    })
    if args.debug:
        print(node_store.root.get_string_for_test_comparison())
    node_store.apply_library(stdlib)

    with (files_root / conf['output_file']).open('w') as f:
        cwdom_to_html_string(stdlib, node_store, f)

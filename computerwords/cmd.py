import argparse
import json
import pathlib
import sys

from collections import namedtuple

from computerwords.cwdom.CWDOMNode import CWDOMDocumentNode, CWDOMRootNode
from computerwords.cwdom.NodeStore import NodeStore
from computerwords.kissup import string_to_cwdom
from computerwords.htmlwriter import cwdom_to_html_string
from computerwords.stdlib import stdlib


DEFAULT_CONFIG = {
    # TODO: auto directory-reading version?
    'file_hierarchy': [
        {'**/*.txt', '**/*.md'},
    ],
    'site_title': 'My Cool Web Site',
    'author': 'Docs McGee',
    'output_file': 'index.html',
}


class DictCascade:
    def __init__(self, *dicts):
        super().__init__()
        self.dicts = list(reversed(dicts))

    def __getitem__(self, k):
        for d in self.dicts:
            if k in d:
                return d[k]
        raise KeyError(k)


DocumentHierarchySubtree = namedtuple(
    'DocumentHierarchySubtree', ['root_path', 'children', 'document_id'])
class DocumentHierarchy:
    def __init__(self, entries):
        super().__init__()
        self.entries = entries

    def __repr__(self):
        return repr(self.entries)

    def __iter__(self):
        return iter(self.entries)


def _glob_or_set_of_globs_to_doc_hierarchy_entry(files_root, entry):
    if isinstance(entry, str):
        globs = sorted(files_root.glob(entry))
        if len(globs) != 1:
            raise ValueError("Handle this case please")
        return DocumentHierarchySubtree(
            globs[0], [], globs[0].relative_to(files_root))
    elif isinstance(entry, dict):
        if len(entry) != 1:
            raise ValueError("One ping only")
        path = (files_root / list(entry.keys())[0]).resolve()
        sub_entries = list(entry.values())[0]
        doc_id = path.relative_to(files_root)
        if not isinstance(sub_entries, list):
            raise ValueError("file_hierarchy subtrees must be lists")
        return DocumentHierarchySubtree(
            path,
            [_glob_or_set_of_globs_to_doc_hierarchy_entry(
                files_root, sub_entry) for sub_entry in sub_entries],
            doc_id)
    else:
        raise ValueError("Unsupported file_hierarchy value: {}".format(entry))


def _add_document_nodes(document_nodes, subtree):
    with subtree.root_path.open() as f:
        doc_node = CWDOMDocumentNode(
            str(subtree.root_path),
            string_to_cwdom(f.read(), stdlib.get_allowed_tags()))
        doc_node.deep_set_document_id(subtree.document_id)
    document_nodes.append(doc_node)
    for child in subtree.children:
        _add_document_nodes(document_nodes, child)
    return document_nodes


def run():
    p = argparse.ArgumentParser()
    p.add_argument('--conf', default="conf.json", type=argparse.FileType('r'))
    args = p.parse_args()

    conf = DictCascade(DEFAULT_CONFIG, json.load(args.conf))
    files_root = pathlib.Path(args.conf.name).parent.resolve()
    doc_hierarchy = DocumentHierarchy([
        _glob_or_set_of_globs_to_doc_hierarchy_entry(files_root, entry)
        for entry in conf['file_hierarchy']
    ])

    document_nodes = []
    for doc in doc_hierarchy:
        _add_document_nodes(document_nodes, doc)
    node_store = NodeStore(CWDOMRootNode(document_nodes))
    node_store.apply_library(stdlib)

    with (files_root / conf['output_file']).open('w') as f:
        cwdom_to_html_string(stdlib, node_store, f)

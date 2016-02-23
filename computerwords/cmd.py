import argparse
import json
import pathlib
import sys

from collections import namedtuple

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
    'DocumentHierarchySubtree', ['root_path', 'children'])
class DocumentHierarchy:
    def __init__(self, entries):
        super().__init__()
        self.entries = entries

    def __repr__(self):
        return repr(self.entries)


def _glob_or_set_of_globs_to_doc_hierarchy_entry(files_root, entry):
    if isinstance(entry, str):
        return sorted(files_root.glob(entry))
    elif isinstance(entry, set):
        return sorted(list(set().union(*[files_root.glob(sub_entry) for sub_entry in entry])))
    elif isinstance(entry, dict):
        if len(entry) != 1:
            raise ValueError("One ping only")
        path = list(entry.keys())[0]
        sub_entries = list(entry.values())[0]
        if not isinstance(sub_entries, list):
            raise ValueError("file_hierarchy subtrees must be lists")
        return DocumentHierarchySubtree(
            path, [_glob_or_set_of_globs_to_doc_hierarchy_entry(
                files_root, sub_entry) for sub_entry in sub_entries])
    else:
        raise ValueError("Unsupported file_hierarchy value: {}".format(entry))


def run():
    p = argparse.ArgumentParser()
    p.add_argument('--conf', default="conf.json", type=argparse.FileType('r'))
    args = p.parse_args()

    conf = DictCascade(DEFAULT_CONFIG, json.load(args.conf))
    files_root = pathlib.Path(args.conf.name).parent.resolve()
    print(conf['file_hierarchy'])
    doc_hierarchy = DocumentHierarchy([
        _glob_or_set_of_globs_to_doc_hierarchy_entry(files_root, entry)
        for entry in conf['file_hierarchy']
    ])
    print(repr(doc_hierarchy))
    # file_paths = 

    node_store = string_to_cwdom(input_str, stdlib.get_allowed_tags())

    node_store.apply_library(stdlib)

    cwdom_to_html_string(stdlib, node_store, sys.stdout)

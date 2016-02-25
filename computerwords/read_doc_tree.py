from collections import namedtuple, OrderedDict
from itertools import chain

from computerwords.cwdom.CWDOMNode import CWDOMDocumentNode


class DocTreeError(Exception): pass


DocSubtree = namedtuple('DocSubtree', ['root_path', 'document_id', 'children'])


def chain_list(lists):
    return list(chain(*lists))


class DocTree:
    def __init__(self, entries):
        super().__init__()
        self.entries = entries

    def __repr__(self):
        return repr(self.entries)

    def __iter__(self):
        return iter(self.entries)

    def __eq__(self, other):
        return type(self) is type(other) and self.entries == other.entries


def _flat_paths_to_sorted_nested_paths(files_root, paths):
    d = OrderedDict()
    for path in paths:
        d[path] = []
        #path = path.relative_to(files_root)
        #print(path.parts)
    return d


def _nested_globs_to_doc_subtree_children(files_root, path_children_pairs):
    return path_children_pairs


def _dict_to_doc_subtree(files_root, entry):
    if len(entry) != 1:
        raise DocTreeError("Only one key per dict allowed")
    path = (files_root / list(entry.keys())[0]).resolve()
    doc_id = path.relative_to(files_root).parts

    sub_entries = list(entry.values())[0]
    if isinstance(sub_entries, str):
        sub_entries = [sub_entries]
    if not isinstance(sub_entries, list):
        raise DocTreeError("Subtree values must be either string or list")

    yield DocSubtree(
        path, doc_id,
        chain_list([_conf_entry_to_doc_subtree(
            files_root, sub_entry) for sub_entry in sub_entries]))


def _conf_entry_to_doc_subtree(files_root, entry):
    if isinstance(entry, str):
        entry = [entry]
    if isinstance(entry, list):
        paths = sorted(chain_list([files_root.glob(glob) for glob in entry]))
        nested_paths = _flat_paths_to_sorted_nested_paths(files_root, paths)
        for path, children in nested_paths.items():
            yield DocSubtree(
                path, path.relative_to(files_root).parts,
                _nested_globs_to_doc_subtree_children(files_root, children))
    elif isinstance(entry, dict):
        yield from _dict_to_doc_subtree(files_root, entry)
    else:
        raise ValueError("Unsupported file_hierarchy value: {}".format(entry))


def doc_subtree_to_cwdom(subtree, get_doc_cwdom):
    """
    get_doc_cwdom(subtree)
    """
    doc_node = CWDOMDocumentNode(
        str(subtree.root_path), get_doc_cwdom(subtree))
    doc_node.deep_set_document_id(subtree.document_id)

    yield doc_node
    for child in subtree.children:
        yield from doc_subtree_to_cwdom(child, get_doc_cwdom)


def read_doc_tree(root_path, file_hierarchy_conf, get_doc_cwdom):
    doc_tree = DocTree(chain_list([
        _conf_entry_to_doc_subtree(root_path, entry)
        for entry in file_hierarchy_conf
    ]))
    document_nodes = chain_list(
        [doc_subtree_to_cwdom(doc, get_doc_cwdom) for doc in doc_tree])
    return doc_tree, document_nodes

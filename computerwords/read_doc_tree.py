from collections import namedtuple, OrderedDict
from functools import cmp_to_key
from itertools import chain

from computerwords.cwdom.nodes import CWDocumentNode


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


def is_name_top(name):
    if name == '__init__.py': return True
    if name.lower().startswith('readme'): return True
    if name.startswith('index.'): return True
    return False


@cmp_to_key
def _path_sort_key(a, b):
    a_name = a.name
    b_name = b.name
    if a.parts[:-1] == b.parts[:-1]:
        if is_name_top(a_name) and not is_name_top(b_name):
            return -1
        elif is_name_top(b_name) and not is_name_top(a_name):
            return 1
        elif a < b:
            return -1
        elif b > a:
            return 1
        else:
            return 0
    else:
        if a < b: return -1
        if b < a: return 1
        return 0


def _get_doc_id(files_root, path):
    rp = path.relative_to(files_root)
    return rp.parts[:-1] + (rp.stem,)


def _dict_to_doc_subtree(files_root, entry):
    if len(entry) != 1:
        raise DocTreeError("Only one key per dict allowed")
    path = (files_root / list(entry.keys())[0]).resolve()

    sub_entries = list(entry.values())[0]
    if isinstance(sub_entries, str):
        sub_entries = [sub_entries]
    if not isinstance(sub_entries, list):
        raise DocTreeError("Subtree values must be either string or list")

    yield DocSubtree(
        path, _get_doc_id(files_root, path),
        chain_list([_conf_entry_to_doc_subtree(
            files_root, sub_entry) for sub_entry in sub_entries]))


def _conf_entry_to_doc_subtree(files_root, entry):
    if isinstance(entry, str):
        entry = [entry]  # fallthrough
    if isinstance(entry, list):
        paths = sorted(
            chain_list([files_root.glob(glob) for glob in entry]),
            key=_path_sort_key)
        for path in paths:
            yield DocSubtree(path, _get_doc_id(files_root, path), [])
    elif isinstance(entry, dict):
        yield from _dict_to_doc_subtree(files_root, entry)
    else:
        raise ValueError("Unsupported file_hierarchy value: {}".format(entry))


def doc_subtree_to_cwdom(subtree, get_doc_cwdom, doc):
    """
    `get_doc_cwdom(subtree, document_id)`
    """
    doc_node = CWDocumentNode(
        str(subtree.root_path),
        get_doc_cwdom(subtree, doc.document_id, str(doc.root_path)))
    doc_node.deep_set_document_id(subtree.document_id)

    yield doc_node
    for child in subtree.children:
        yield from doc_subtree_to_cwdom(child, get_doc_cwdom, doc)


def read_doc_tree(root_path, file_hierarchy_conf, get_doc_cwdom):
    doc_tree = DocTree(chain_list([
        _conf_entry_to_doc_subtree(root_path, entry)
        for entry in file_hierarchy_conf
    ]))
    document_nodes = chain_list(
        [doc_subtree_to_cwdom(doc, get_doc_cwdom, doc)
        for doc in doc_tree])
    return doc_tree, document_nodes

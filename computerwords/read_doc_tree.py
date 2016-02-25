from collections import namedtuple
from itertools import chain

from computerwords.cwdom.CWDOMNode import CWDOMDocumentNode


class DocTreeError(Exception): pass


DocSubtree = namedtuple('DocSubtree', ['root_path', 'document_id', 'children'])


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


def _glob_or_set_of_globs_to_doc_hierarchy_entry(files_root, entry):
    if isinstance(entry, str):
        globs = sorted(files_root.glob(entry))
        if len(globs) != 1:
            raise ValueError("Handle this case please")
        return DocSubtree(
            globs[0], str(globs[0].relative_to(files_root)), [])
    elif isinstance(entry, dict):
        if len(entry) != 1:
            raise DocTreeError("Only one key per dict allowed")
        path = (files_root / list(entry.keys())[0]).resolve()
        doc_id = str(path.relative_to(files_root))

        sub_entries = list(entry.values())[0]
        if isinstance(sub_entries, str):
            sub_entries = [sub_entries]
        if not isinstance(sub_entries, list):
            raise DocTreeError("Subtree values must be either string or list")

        return DocSubtree(
            path, doc_id,
            [_glob_or_set_of_globs_to_doc_hierarchy_entry(
                files_root, sub_entry) for sub_entry in sub_entries])
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
    doc_tree = DocTree([
        _glob_or_set_of_globs_to_doc_hierarchy_entry(root_path, entry)
        for entry in file_hierarchy_conf
    ])
    document_nodes = list(
        chain(*[doc_subtree_to_cwdom(doc, get_doc_cwdom) for doc in doc_tree]))
    return doc_tree, document_nodes

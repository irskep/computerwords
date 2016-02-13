from collections import OrderedDict, namedtuple
from computerwords.cwdom.CWDOMNode import CWDDOMEndOfInputNode


"""
As the tree is being traversed, each node will be annotated with its traversal
order encoded in a tuple key like (1, 2, 6, 8, 0).

When you invalidate a node, it will be added to a list like this:
(traversal_order_key, node)

If a node X has a child A, and node X has a traversal key of (1, 2), and A is
node X's first child, then node A's traversal key will be (1, 2, 0).

When the end-of-source node is reached by NodeStore, the invalidation list will
be sorted by traversal key, and all processors for each node will be called
again.
"""


TOC_TAG_NAME = 'table_of_contents'
TOCEntry = namedtuple('TOCEntry', ['level', 'text'])


def tree_to_text(node_store, node):
    segments = []
    for n in node_store.preorder_traversal(node):
        if n.name == 'Text':
            segments.append(n.text)
    return ''.join(segments)


def _add_toc_data_if_not_exists(node_store):
    node_store.library_data.setdefault('toc_entries_is_complete', False)
    node_store.library_data.setdefault('toc_entries', [])


def add_table_of_contents(library):
    @library.end_processor
    def process_end(node_store, end_node):
        for node in node_store.get_nodes(TOC_TAG_NAME):
            node_store.invalidate(node)
    node_store.library_data['toc_entries_is_complete'] = True

    @library.processor('Document')
    def process_document(node_store, node):
        _add_toc_data_if_not_exists(node_store)
        node_store.library_data['toc_entries'].append(TOCEntry(0, node.path))

    name_to_level = {'h' + str(i): i for i in range(1, 7)}
    @library.processor('h1')
    @library.processor('h2')
    @library.processor('h3')
    @library.processor('h4')
    @library.processor('h5')
    @library.processor('h6')
    def process_heading(node_store, node):
        _add_toc_data_if_not_exists(node_store)
        node_store.library_data['toc_entries'].append(
            TOCEntry(name_to_level[node.name], tree_to_text(node)))

    @library.processor(TOC_TAG_NAME)

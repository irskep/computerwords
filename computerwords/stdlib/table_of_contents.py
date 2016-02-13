import logging
from collections import OrderedDict, namedtuple, deque
from computerwords.cwdom import (
    CWDDOMEndOfInputNode,
    CWDOMTagNode,
)


log = logging.getLogger(__name__)


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


HEADER_TAG_NAMES = {'h' + str(i) for i in range(1, 7)}
TOC_TAG_NAME = 'table_of_contents'
TOCEntry = namedtuple('TOCEntry', ['level', 'text', 'ref_id'])


def tree_to_text(node_store, node):
    segments = []
    for n in node_store.preorder_traversal(node):
        if n.name == 'Text':
            segments.append(n.text)
    return ''.join(segments)


def _add_toc_data_if_not_exists(node_store):
    node_store.library_data.setdefault('toc_entries_is_complete', False)
    node_store.library_data.setdefault('toc_entries', [])
    node_store.library_data.setdefault('toc_entry_to_sequence', None)


def _entries_to_nested_list(entries):
    # 0 MyDoc.bb mydoc
    # 1 "A header" a-header
    # 2 "subsection" subsection
    # 1 "Another header"
    # 3 "subsubsection" subsubsection
    # 0 AnotherDoc.bb
    # 3 "asdf" asdf
    # [
    #   ("MyDoc.bb", [
    #       ("A header", [
    #           ("subsection", [])
    #       ]),
    #       ("Another header", [
    #           ("subsubsection", [])
    #       ]),
    #   ]),
    #   ("AnotherDoc.bb", [("asdf", [])]),
    # ]
    top_level_list = []
    stack = deque((TOCEntry(-1, None, None), top_level_list))
    for entry in entries:
        parent_entry, list_to_add_to = level_stack[-1]
        while entry.level <= parent_entry.level:
            parent_entry, list_to_add_to = level_stack.pop()
        list_to_add_to.append(entry)
        stack.append((entry, []))
    return top_level_list


def _store_entry_to_sequence(nested_list, entry_to_sequence, sequence_so_far):
    for i, (child, grandchildren) in enumerate(nested_list):
        sequence = sequence_so_far + [i + 1]
        entry_to_sequence[child] = sequence
        _store_entry_to_sequence(grandchildren, entry_to_sequence, sequence)


# [(TOCEntry, [children]), ...]
def _nested_list_to_nodes(entry_children_pairs):
    return [
        CWDOMTagNode('li', [
            CWDOMLinkNode(entry.ref_id, [
                CWDOMTagNode('div', [
                    CWDOMTextNode(entry.text)
                ])
            ])
        ] + _nested_list_to_nodes(children))
        for entry, children in entry_children_pairs
    ]


def _get_are_all_headers_valid(node_store):
    for name in HEADER_TAG_NAMES:
        for node in node_store.get_nodes(name):
            if not node_store.get_is_valid(node):
                return False
    return True


def add_table_of_contents(library):
    @library.end_processor
    def process_end(node_store, end_node):
        _add_toc_data_if_not_exists(node_store)
        if node_store.library_data['toc_entries_is_complete']:
            log.debug('End node: doing nothing')
        elif _get_are_all_headers_valid(node_store):
            log.debug('End node: mark entries-complete; invalidate')
            node_store.library_data['toc_entries_is_complete'] = True

            # now go back and fix all the [table_of_contents /] nodes
            for node in node_store.get_nodes(TOC_TAG_NAME):
                node_store.invalidate(node)
        else:
            log.debug("End node: headers aren't ready, invalidate for another pass")
            # node_store should have validated this node already; invalidating
            # it will add it to the next pass.
            node_store.invalidate(end_node)

    @library.processor('Document')
    def process_document(node_store, node):
        _add_toc_data_if_not_exists(node_store)
        log.debug('Document node: add TOC entry')
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
        text = tree_to_text(node)
        ref_id = node_store.get_ref_id(text)  # might be identical
        entry = TOCEntry(name_to_level[node.name], text, ref_id)
        if node_store.library_data['toc_entry_to_sequence']:
            log.debug('Header node: add number and anchor')
            number = '.'.join(node_store.library_data['toc_entry_to_sequence'][entry])
            _prepend_text_to_node_children(node_store, node, str(number) + ' ')
            anchor = CWDOMAnchorNode(entry.ref_id)
            node_store.wrap_node(node, )
        else:
            log.debug('Header node: add TOC entry')
            node_store.library_data['toc_entries'].append(entry)

    @library.processor(TOC_TAG_NAME)
    def process_toc(node_store, node):
        _add_toc_data_if_not_exists(node_store)

        if not node_store.library_data['toc_entries_is_complete']:
            return

        anchor = CWDOMAnchorNode('table-of-contents')
        node_store.replace(node, anchor)

        ul = CWDOMTagNode('ul', kwargs={'class': 'table-of-contents'})
        # don't add ul to node_store until it has all its children, to cut
        # down on the number of add_child() calls in this function. (add_child
        # recursively adds the node's children to node_store and invalidates
        # them.)

        k = None
        entries_by_document = {}
        for entry in node_store.library_data['toc_entries']:
            if entry.level == 0:
                k = entry.path
                entries_by_document[k] = []
            else:
                entries_by_document[k].append(entry)

        output_order = sorted(entries_by_document.keys())
        node_store.library_data['toc_entry_to_number'] = {}
        for i, k in output_order:
            nested_list = _entries_to_nested_list(entries_by_document[k])
            _store_entry_to_sequence(
                nested_list, node_store.library_data['toc_entry_to_sequence'], [i])
            ul.children = _nested_list_to_nodes(nested_list)

        node_store.add_child(anchor, ul)

        for name in HEADER_TAG_NAMES:
            for node in node_store.get_nodes(name):
                node_store.invalidate(node)


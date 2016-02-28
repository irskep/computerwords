import logging
from collections import OrderedDict, namedtuple, deque
from computerwords.cwdom.CWDOMNode import (
    CWDOMAnchorNode,
    CWDOMLinkNode,
    CWDOMTagNode,
    CWDOMTextNode,
)


log = logging.getLogger(__name__)


HEADER_TAG_NAMES = {'h' + str(i) for i in range(1, 7)}
NAME_TO_LEVEL = {'h' + str(i): i for i in range(1, 7)}
TOC_TAG_NAME = 'table-of-contents'
TOCEntry = namedtuple('TOCEntry', ['level', 'heading_node', 'ref_id'])


def tree_to_text(node_store, node):
    segments = []
    for n in node_store.preorder_traversal(node):
        if n.name == 'Text':
            segments.append(n.text)
    return ''.join(segments)


### helpers ###


def _add_toc_data_if_not_exists(node_store):
    node_store.processor_data.setdefault('toc_nodes', [])
    node_store.processor_data.setdefault('toc_heading_nodes', [])


def _node_to_toc_entry(node_store, node):
    text = tree_to_text(node_store, node)
    ref_id = node_store.text_to_ref_id(text)  # might be identical
    return TOCEntry(NAME_TO_LEVEL[node.name], node, ref_id)


# [(TOCEntry, [children]), ...] -> DOM
def _format_entry_number(entry_to_number, entry):
    return '.'.join(str(n) for n in entry_to_number[entry])

def _nested_list_to_node(entry_to_number, entry_children_pairs):
    def make_li(entry, children):
        li_contents = [
            CWDOMLinkNode(entry.ref_id, entry.heading_node.deepcopy().children)
        ]
        if children:
            li_contents.append(_nested_list_to_node(entry_to_number, children))
        return CWDOMTagNode('li', {}, li_contents)
    return CWDOMTagNode('ol', {}, [
        make_li(entry, children) for entry, children in entry_children_pairs
    ])


def _entries_to_nested_list(entries):
    top_level_list = []
    stack = deque([(TOCEntry(-1, None, None), top_level_list)])
    for entry in entries:
        parent_entry, list_to_add_to = stack[-1]
        while entry.level <= parent_entry.level:
            parent_entry, list_to_add_to = stack.pop()
        pair = (entry, [])
        list_to_add_to.append(pair)
        stack.append(pair)
    return top_level_list


def _store_entry_to_sequence(nested_list, entry_to_sequence, sequence_so_far):
    for i, (child, grandchildren) in enumerate(nested_list):
        sequence = sequence_so_far + (i + 1,)
        entry_to_sequence[child] = sequence
        _store_entry_to_sequence(grandchildren, entry_to_sequence, sequence)


def add_table_of_contents(library):
    """
    Collects all `h1`, `h2`, etc. tags in a tree, which
    you can display with `[table-of-contents /]`.

    Currently they are displayed in alphabetical order. 

    The original header tags will be modified to include anchors (to which
    the TOC table will link) and heading numbers.

    # Planned features

    ## Explicit ordering of documents

    ```
    [table-of-contents]
        doc_1.txt
        doc_2.txt
    [/table-of-contents]
    ```

    ## Scoped TOC instances (for sidebars)

    ```
    [# only show entries under doc_1.txt #]
    [table-of-contents scope="doc_1.txt" /]
    ```
    """

    @library.processor('h1')
    @library.processor('h2')
    @library.processor('h3')
    @library.processor('h4')
    @library.processor('h5')
    @library.processor('h6')
    def process_header(node_store, node):
        if node.kwargs.get('skip_toc', '').lower() == 'true':
            return
        _add_toc_data_if_not_exists(node_store)
        node_store.processor_data['toc_heading_nodes'].append(node)
        entry = _node_to_toc_entry(node_store, node)
        anchor = CWDOMAnchorNode(
            entry.ref_id, kwargs={'class': 'header-anchor'})
        node_store.wrap_node(node, anchor)

        # associate this entry with both nodes for convenience
        node.data['toc_entry'] = entry
        anchor.data['toc_entry'] = entry

    @library.processor('Document')
    def process_document(node_store, node):
        _add_toc_data_if_not_exists(node_store)
        node.data['toc_entries'] = [
            child.data['toc_entry']
            for child in node.children
            if 'toc_entry' in child.data
        ]

    @library.processor(TOC_TAG_NAME)
    def process_toc(node_store, node):
        _add_toc_data_if_not_exists(node_store)
        node_store.processor_data['toc_nodes'].append(node)

    @library.processor('Root')
    def process_root(node_store, node):
        _add_toc_data_if_not_exists(node_store)

        doc_to_entries = {
            doc_node.path: doc_node.data['toc_entries']
            for doc_node in node.children
            if doc_node.name == 'Document'
        }

        # TODO: derive from table-of-contents tag contents?
        sorted_paths = sorted(doc_to_entries.keys())
        top_level_entries = []
        for path in sorted_paths:
            top_level_entries.extend(
                _entries_to_nested_list(doc_to_entries[path]))

        entry_to_number = {}
        _store_entry_to_sequence(top_level_entries, entry_to_number, ())

        # TODO: require different TOC subsets per tag, like sphinx?
        for toc_node in node_store.processor_data['toc_nodes']:
            node_store.replace_subtree(
                toc_node,
                CWDOMTagNode('nav', {'class': 'table-of-contents'}, [
                    _nested_list_to_node(entry_to_number, top_level_entries),
                ]))

        # optional: insert heading numbers
        # for heading_node in node_store.processor_data['toc_heading_nodes']:
        #     number = _format_entry_number(
        #         entry_to_number, heading_node.data['toc_entry'])
        #     node_store.insert_subtree(
        #         heading_node,
        #         0,
        #         CWDOMTextNode(number + ' '))

import logging
from collections import OrderedDict, namedtuple, deque
from computerwords.cwdom.nodes import (
    CWAnchorNode,
    CWLinkNode,
    CWTagNode,
    CWTextNode,
)


log = logging.getLogger(__name__)


HEADER_TAG_NAMES = {'h' + str(i) for i in range(1, 7)}
NAME_TO_LEVEL = {'h' + str(i): i for i in range(1, 7)}
TOC_TAG_NAME = 'table-of-contents'
TOCEntry = namedtuple('TOCEntry', ['level', 'heading_node', 'ref_id'])


def tree_to_text(tree, node):
    segments = []
    for n in tree.preorder_traversal(node):
        if n.name == 'Text':
            segments.append(n.text)
    return ''.join(segments)


### helpers ###


def _add_toc_data_if_not_exists(tree):
    tree.processor_data.setdefault('toc_nodes', [])
    tree.processor_data.setdefault('toc_heading_nodes', [])


def _node_to_toc_entry(tree, node):
    text = tree_to_text(tree, node)
    ref_id = tree.text_to_ref_id(text)  # might be identical
    return TOCEntry(NAME_TO_LEVEL[node.name], node, ref_id)


# [(TOCEntry, [children]), ...] -> DOM
def _format_entry_number(entry_to_number, entry):
    return '.'.join(str(n) for n in entry_to_number[entry])

def _nested_list_to_node(entry_to_number, entry_children_pairs, max_depth=3):
    def make_li(entry, children):
        li_contents = [
            CWLinkNode(entry.ref_id, entry.heading_node.deepcopy().children)
        ]
        if children and max_depth > 1:
            li_contents.append(
                _nested_list_to_node(entry_to_number, children, max_depth - 1))
        return CWTagNode('li', {}, li_contents)
    return CWTagNode('ol', {}, [
        make_li(entry, children) for entry, children in entry_children_pairs
    ])


def _entries_to_nested_list(entries):
    top_level_list = []
    stack = deque([(TOCEntry(-1, None, None), top_level_list)])
    for entry in entries:
        parent_entry, list_to_add_to = stack[-1]
        while entry.level <= parent_entry.level:
            stack.pop()
            parent_entry, list_to_add_to = stack[-1]
        pair = (entry, [])
        list_to_add_to.append(pair)
        stack.append(pair)
    return top_level_list


def _store_entry_to_sequence(nested_list, entry_to_sequence, sequence_so_far):
    for i, (child, grandchildren) in enumerate(nested_list):
        sequence = sequence_so_far + (i + 1,)
        entry_to_sequence[child] = sequence
        _store_entry_to_sequence(grandchildren, entry_to_sequence, sequence)


def _doc_tree_to_sorted_paths(doc_tree):
    items = []
    for entry in doc_tree:
        items.append(str(entry.root_path))
        items += _doc_tree_to_sorted_paths(entry.children)
    return items


def _preorder_traversal_of_nested_list(entries):
    for (entry, children) in entries:
        yield entry
        for child in children:
            yield from _preorder_traversal_of_nested_list(children)


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
    def process_header(tree, node):
        if node.kwargs.get('skip_toc', '').lower() == 'true':
            return
        _add_toc_data_if_not_exists(tree)
        tree.processor_data['toc_heading_nodes'].append(node)
        entry = _node_to_toc_entry(tree, node)
        anchor = CWAnchorNode(
            entry.ref_id, kwargs={'class': 'header-anchor'})
        tree.wrap_node(node, anchor)

        # associate this entry with both nodes for convenience
        node.data['toc_entry'] = entry
        anchor.data['toc_entry'] = entry

    @library.processor('Document')
    def process_document(tree, node):
        _add_toc_data_if_not_exists(tree)
        node.data['toc_entries'] = [
            child.data['toc_entry']
            for child in node.children
            if 'toc_entry' in child.data
        ]

    @library.processor(TOC_TAG_NAME)
    def process_toc(tree, node):
        _add_toc_data_if_not_exists(tree)
        tree.processor_data['toc_nodes'].append(node)

    @library.processor('Root')
    def process_root(tree, node):
        _add_toc_data_if_not_exists(tree)

        doc_path_to_entries = {
            doc_node.path: doc_node.data['toc_entries']
            for doc_node in node.children
            if doc_node.name == 'Document'
        }

        ### compute TOC ###

        if tree.env and 'doc_tree' in tree.env:
            sorted_paths = _doc_tree_to_sorted_paths(
                tree.env['doc_tree'])
        else:
            sorted_paths = sorted(doc_path_to_entries.keys())
        top_level_entries = []
        for path in sorted_paths:
            top_level_entries.extend(
                _entries_to_nested_list(doc_path_to_entries[path]))

        tree.processor_data['toc'] = top_level_entries

        ### put TOC in tree ###

        entry_to_number = {}
        _store_entry_to_sequence(top_level_entries, entry_to_number, ())

        for toc_node in tree.processor_data['toc_nodes']:
            max_depth = 3
            try:
                max_depth = int(toc_node.kwargs.get('maxdepth', '3'))
            except ValueError:
                pass
            assert(max_depth > 0)

            tree.replace_subtree(
                toc_node,
                CWTagNode('nav', {'class': 'table-of-contents'}, [
                    _nested_list_to_node(
                        entry_to_number, top_level_entries, max_depth),
                ]))

        ### add next/prev data to docs ###

        path_to_doc = {
            doc_node.path: doc_node
            for doc_node in node.children
            if doc_node.name == 'Document'
        }

        last_doc = None
        for path in sorted_paths:
            doc = path_to_doc[path]
            if last_doc:
                if doc_path_to_entries[last_doc.path]:
                    doc.data['nav_previous_entry'] = doc_path_to_entries[last_doc.path][0]
                if doc_path_to_entries[doc.path]:
                    last_doc.data['nav_next_entry'] = doc_path_to_entries[doc.path][0]
            last_doc = doc

        # optional: insert heading numbers
        # for heading_node in tree.processor_data['toc_heading_nodes']:
        #     number = _format_entry_number(
        #         entry_to_number, heading_node.data['toc_entry'])
        #     tree.insert_subtree(
        #         heading_node,
        #         0,
        #         CWTextNode(number + ' '))

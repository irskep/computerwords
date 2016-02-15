import logging
import unittest
from textwrap import dedent

from computerwords.cwdom.NodeStore import NodeStore
from computerwords.cwdom.CWDOMNode import *
from computerwords.library import Library


log = logging.getLogger(__name__)


END = CWDOMEndOfInputNode.NAME


def strip(s):
    return dedent(s)[1:-1]


class TestNode(CWDOMNode):
    def __init__(self, name, **data):
        super().__init__(name)
        self.data = data


def log_tree(ns):
    logging.basicConfig(level=logging.DEBUG)
    log.debug('\n' + ns.root.get_string_for_test_comparison())


class TestLibrary(Library):
    def __init__(self):
        super().__init__()
        self.visit_history = []

        record = lambda node_store, node: self.visit_history.append(node.name)

        self.processor('Root', record)
        self.processor('Document', record)
        self.processor('a', record)
        self.processor('b', record)
        self.processor('c', record)
        self.processor('d', record)
        self.processor('e', record)
        self.processor('a_child', record)

        def invalidate_a(node_store, node):
            for a in node_store.get_nodes('a'):
                node_store.invalidate(a)
        self.processor('invalidate_a', record)
        self.processor('invalidate_a', invalidate_a)

        def add_own_child(node_store, node):
            node_store.add_node(node, CWDOMNode('a_child'))
        self.processor('add_own_child', record)
        self.processor('add_own_child', add_own_child)

        def add_child_to_a(node_store, node):
            i = node.data.get('i', None)
            for a in node_store.get_nodes('a'):
                node_store.add_node(a, CWDOMNode('a_child'), i)
        self.processor('add_child_to_a', record)
        self.processor('add_child_to_a', add_child_to_a)

        self.end_processor(record)


class TestNodeStore(unittest.TestCase):
    def assertTraversalKeysAreConsistent(self, ns, debug=False):
        flat_nodes = list(ns.preorder_traversal(ns.root))
        pairs = [(ns.get_traversal_key(n), n) for n in flat_nodes]
        if debug:
            for pair in pairs: print(pair)
            print('-')
            for pair in sorted(pairs): print(pair)
        self.assertEqual(
            list(ns.preorder_traversal(ns.root)),
            [pair[1] for pair in sorted(pairs)])

    def test_simple(self):
        # most tests won't need to build the tree this tedious way. this
        # particular test needs to verify the traversal key sort order.
        a = CWDOMNode('a')
        b = CWDOMNode('b')
        c = CWDOMNode('c')
        doc = CWDOMDocumentNode('doc')
        doc.set_children([a, b, c])
        root = CWDOMRootNode()
        root.set_children([doc])
        flat_nodes = [a, c, b, doc, root]

        ns = NodeStore(root)
        library = TestLibrary()
        ns.apply_library(library)
        self.assertEqual(library.visit_history, [
            'Root', 'Document', 'a', 'b', 'c', END
        ])

        # now that the node store has traversed the tree, we can easily sort
        # the nodes by their preorder traversal position
        reconstructed_pairs = sorted([
            (ns.get_traversal_key(n), n) for n in flat_nodes
        ])
        self.assertEqual(
            [pair[1] for pair in reconstructed_pairs],
            [root, doc, a, b, c])

    def test_invalidate(self):
        ns = NodeStore(CWDOMRootNode([
            CWDOMDocumentNode('doc', [
                CWDOMNode('a'),
                CWDOMNode('b'),
                CWDOMNode('invalidate_a')
            ])
        ]))
        library = TestLibrary()
        ns.apply_library(library)
        self.assertEqual(library.visit_history, [
            'Root', 'Document', 'a', 'b', 'invalidate_a',
            END,
            'a'
        ])

    def test_add_own_child(self):
        ns = NodeStore(CWDOMRootNode([
            CWDOMDocumentNode('doc', [
                CWDOMNode('a'),
                CWDOMNode('b'),
                TestNode('add_own_child')
            ])
        ]))
        library = TestLibrary()
        ns.apply_library(library)
        self.assertEqual(library.visit_history, [
            'Root', 'Document', 'a', 'b', 'add_own_child', 'a_child',
            END,
        ])

    def test_forward_child(self):
        ns = NodeStore(CWDOMRootNode([
            CWDOMDocumentNode('doc', [
                TestNode('add_child_to_a'),
                CWDOMNode('b'),
                CWDOMNode('a'),
            ])
        ]))
        library = TestLibrary()
        ns.apply_library(library)
        self.assertEqual(library.visit_history, [
            'Root', 'Document', 'add_child_to_a', 'b', 'a', 'a_child',
            END,
        ])

    def test_backward_child(self):
        ns = NodeStore(CWDOMRootNode([
            CWDOMDocumentNode('doc', [
                CWDOMNode('a'),
                CWDOMNode('b'),
                TestNode('add_child_to_a'),
            ])
        ]))
        library = TestLibrary()
        ns.apply_library(library)
        self.assertEqual(library.visit_history, [
            'Root', 'Document', 'a', 'b', 'add_child_to_a', END, 'a_child'
        ])

    def test_add_at_end(self):
        ns = NodeStore(CWDOMRootNode([
            CWDOMDocumentNode('doc', [
                CWDOMNode('a', [
                    CWDOMNode('b', []),
                    CWDOMNode('c', []),
                ]),
                TestNode('add_child_to_a'),
            ])
        ]))
        library = TestLibrary()
        ns.apply_library(library)
        self.assertEqual(library.visit_history, [
            'Root', 'Document', 'a', 'b', 'c', 'add_child_to_a', END, 'a_child'
        ])
        self.assertEqual(ns.root.get_string_for_test_comparison(), strip("""
            Root()
              Document()
                a()
                  b()
                  c()
                  a_child()
                add_child_to_a()
              CWEnd()
        """))
        self.assertTraversalKeysAreConsistent(ns)

    def test_add_at_beginning(self):
        ns = NodeStore(CWDOMRootNode([
            CWDOMDocumentNode('doc', [
                CWDOMNode('a', [
                    CWDOMNode('b', []),
                    CWDOMNode('c', []),
                ]),
                TestNode('add_child_to_a', i=0),
            ])
        ]))
        library = TestLibrary()
        ns.apply_library(library)
        self.assertEqual(library.visit_history, [
            'Root', 'Document', 'a', 'b', 'c', 'add_child_to_a', END, 'a_child'
        ])
        self.assertEqual(ns.root.get_string_for_test_comparison(), strip("""
            Root()
              Document()
                a()
                  a_child()
                  b()
                  c()
                add_child_to_a()
              CWEnd()
        """))
        self.assertTraversalKeysAreConsistent(ns)

    def test_add_in_middle(self):
        ns = NodeStore(CWDOMRootNode([
            CWDOMDocumentNode('doc', [
                CWDOMNode('a', [
                    CWDOMNode('b', []),
                    CWDOMNode('c', []),
                ]),
                TestNode('add_child_to_a', i=1),
            ])
        ]))
        library = TestLibrary()
        ns.apply_library(library)
        self.assertEqual(library.visit_history, [
            'Root', 'Document', 'a', 'b', 'c', 'add_child_to_a', END, 'a_child'
        ])
        self.assertEqual(ns.root.get_string_for_test_comparison(), strip("""
            Root()
              Document()
                a()
                  b()
                  a_child()
                  c()
                add_child_to_a()
              CWEnd()
        """))
        self.assertTraversalKeysAreConsistent(ns)

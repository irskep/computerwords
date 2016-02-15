import logging
import unittest
from textwrap import dedent

from computerwords.cwdom.NodeStore import NodeStore, NodeStoreConsistencyError
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


class LibraryForTesting(Library):
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
        self.processor('wrapper', record)
        self.processor('replacement', record)

        self.processor('invalidate_a', record)
        @self.processor('invalidate_a')
        def invalidate_a(node_store, node):
            for a in node_store.get_nodes('a'):
                node_store.invalidate(a)

        self.processor('add_own_child', record)
        @self.processor('add_own_child')
        def add_own_child(node_store, node):
            node_store.add_node(node, CWDOMNode('a_child'))

        self.processor('add_child_to_a', record)
        @self.processor('add_child_to_a')
        def add_child_to_a(node_store, node):
            i = node.data.get('i', None)
            for a in node_store.get_nodes('a'):
                node_store.add_node(a, CWDOMNode('a_child'), i)

        self.processor('wrap_self', record)
        @self.processor('wrap_self')
        def wrap_self(node_store, node):
            node_store.wrap_node(node, CWDOMNode('wrapper'))

        self.processor('replace_self', record)
        @self.processor('replace_self')
        def replace_self(node_store, node):
            node_store.replace_node(node, CWDOMNode('replacement'))

        self.processor('remove_self', record)
        @self.processor('remove_self')
        def replace_self(node_store, node):
            node_store.remove_node(node)

        self.processor('replace_a', record)
        @self.processor('replace_a')
        def replace_a(node_store, node):
            for a in node_store.get_nodes('a'):
                node_store.replace_node(a, CWDOMNode('replacement'))

        self.processor('remove_a', record)
        @self.processor('remove_a')
        def replace_a(node_store, node):
            for a in node_store.get_nodes('a'):
                node_store.remove_node(a)

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

    def assertTreeIsConsistent(self, node):
        for child in node.children:
            self.assertEqual(child.get_parent(), node)
            self.assertTreeIsConsistent(child)

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
        library = LibraryForTesting()
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
        library = LibraryForTesting()
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
        library = LibraryForTesting()
        ns.apply_library(library)
        self.assertEqual(library.visit_history, [
            'Root', 'Document', 'a', 'b', 'add_own_child', 'a_child',
            END,
        ])

    def test_add_forward(self):
        ns = NodeStore(CWDOMRootNode([
            CWDOMDocumentNode('doc', [
                TestNode('add_child_to_a'),
                CWDOMNode('b'),
                CWDOMNode('a'),
            ])
        ]))
        library = LibraryForTesting()
        ns.apply_library(library)
        self.assertEqual(library.visit_history, [
            'Root', 'Document', 'add_child_to_a', 'b', 'a', 'a_child',
            END,
        ])

    def test_add_backward(self):
        ns = NodeStore(CWDOMRootNode([
            CWDOMDocumentNode('doc', [
                CWDOMNode('a'),
                CWDOMNode('b'),
                TestNode('add_child_to_a'),
            ])
        ]))
        library = LibraryForTesting()
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
        library = LibraryForTesting()
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
        library = LibraryForTesting()
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
        library = LibraryForTesting()
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

    def test_replace_self(self):
        ns = NodeStore(CWDOMRootNode([
            CWDOMDocumentNode('doc', [
                CWDOMNode('replace_self'),
            ])
        ]))
        library = LibraryForTesting()
        ns.apply_library(library)
        self.assertEqual(library.visit_history, [
            'Root', 'Document', 'replace_self', END, 'replacement'
        ])
        self.assertEqual(ns.root.get_string_for_test_comparison(), strip("""
            Root()
              Document()
                replacement()
              CWEnd()
        """))
        self.assertTraversalKeysAreConsistent(ns)

    def test_replace_ahead(self):
        ns = NodeStore(CWDOMRootNode([
            CWDOMDocumentNode('doc', [
                CWDOMNode('replace_a'),
                CWDOMNode('b', [
                    CWDOMNode('a'),
                ]),
            ])
        ]))
        library = LibraryForTesting()
        ns.apply_library(library)
        self.assertEqual(library.visit_history, [
            'Root', 'Document', 'replace_a', 'b', 'replacement', END,
        ])
        self.assertEqual(ns.root.get_string_for_test_comparison(), strip("""
            Root()
              Document()
                replace_a()
                b()
                  replacement()
              CWEnd()
        """))
        self.assertTraversalKeysAreConsistent(ns)

    def test_replace_behind(self):
        ns = NodeStore(CWDOMRootNode([
            CWDOMDocumentNode('doc', [
                CWDOMNode('b', [
                    CWDOMNode('a'),
                ]),
                CWDOMNode('replace_a'),
            ])
        ]))
        library = LibraryForTesting()
        ns.apply_library(library)
        self.assertEqual(library.visit_history, [
            'Root', 'Document', 'b', 'a', 'replace_a', END, 'replacement'
        ])
        self.assertEqual(ns.root.get_string_for_test_comparison(), strip("""
            Root()
              Document()
                b()
                  replacement()
                replace_a()
              CWEnd()
        """))
        self.assertTraversalKeysAreConsistent(ns)

    def test_remove_self(self):
        ns = NodeStore(CWDOMRootNode([
            CWDOMDocumentNode('doc', [
                CWDOMNode('remove_self'),
            ])
        ]))
        library = LibraryForTesting()
        ns.apply_library(library)
        self.assertEqual(library.visit_history, [
            'Root', 'Document', 'remove_self', END,
        ])
        self.assertEqual(ns.root.get_string_for_test_comparison(), strip("""
            Root()
              Document()
              CWEnd()
        """))
        self.assertTraversalKeysAreConsistent(ns)

    def test_remove_ahead(self):
        ns = NodeStore(CWDOMRootNode([
            CWDOMDocumentNode('doc', [
                CWDOMNode('remove_a'),
                CWDOMNode('b', [
                    CWDOMNode('a'),
                ]),
            ])
        ]))
        library = LibraryForTesting()
        ns.apply_library(library)
        self.assertEqual(library.visit_history, [
            'Root', 'Document', 'remove_a', 'b', END,
        ])
        self.assertEqual(ns.root.get_string_for_test_comparison(), strip("""
            Root()
              Document()
                remove_a()
                b()
              CWEnd()
        """))
        self.assertTraversalKeysAreConsistent(ns)

    def test_remove_behind(self):
        ns = NodeStore(CWDOMRootNode([
            CWDOMDocumentNode('doc', [
                CWDOMNode('b', [
                    CWDOMNode('a'),
                ]),
                CWDOMNode('remove_a'),
            ])
        ]))
        library = LibraryForTesting()
        ns.apply_library(library)
        self.assertEqual(library.visit_history, [
            'Root', 'Document', 'b', 'a', 'remove_a', END,
        ])
        self.assertEqual(ns.root.get_string_for_test_comparison(), strip("""
            Root()
              Document()
                b()
                remove_a()
              CWEnd()
        """))
        self.assertTraversalKeysAreConsistent(ns)


class TestNodeStoreSiblingMutationErrors(unittest.TestCase):

    def test_replace_ahead(self):
        ns = NodeStore(CWDOMRootNode([
            CWDOMDocumentNode('doc', [
                CWDOMNode('replace_a'),
                CWDOMNode('a'),
            ])
        ]))
        with self.assertRaises(NodeStoreConsistencyError):
            ns.apply_library(LibraryForTesting())

    def test_replace_behind(self):
        ns = NodeStore(CWDOMRootNode([
            CWDOMDocumentNode('doc', [
                CWDOMNode('a'),
                CWDOMNode('replace_a'),
            ])
        ]))
        with self.assertRaises(NodeStoreConsistencyError):
            ns.apply_library(LibraryForTesting())

    def test_remove_ahead(self):
        ns = NodeStore(CWDOMRootNode([
            CWDOMDocumentNode('doc', [
                CWDOMNode('remove_a'),
                CWDOMNode('a'),
            ])
        ]))
        with self.assertRaises(NodeStoreConsistencyError):
            ns.apply_library(LibraryForTesting())

    def test_remove_behind(self):
        ns = NodeStore(CWDOMRootNode([
            CWDOMDocumentNode('doc', [
                CWDOMNode('a'),
                CWDOMNode('remove_a'),
            ])
        ]))
        with self.assertRaises(NodeStoreConsistencyError):
            ns.apply_library(LibraryForTesting())

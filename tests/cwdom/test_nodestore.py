import logging
import unittest
from collections import defaultdict

from tests.CWTestCase import CWTestCase
from computerwords.cwdom.NodeStore import NodeStore, NodeStoreConsistencyError
from computerwords.cwdom.CWDOMNode import *
from computerwords.library import Library


log = logging.getLogger(__name__)


class TestNode(CWDOMNode):
    def __init__(self, name, **data):
        super().__init__(name)
        self.data = data


class LibraryForTesting(Library):
    def __init__(self):
        super().__init__()
        self.visit_history = []
        self.name_to_nodes = defaultdict(list)

        def record(node_store, node):
            self.visit_history.append(node.name)
            self.name_to_nodes[node.name].append(node)

        BARE_NAMES = {
            'Root', 'Document',
            'a', 'b',
            'a_child', 'wrapper', 'contents', 'replacement',
        }
        for node_name in BARE_NAMES:
            self.processor(node_name, record)

        self.processor('dirty_a', record)
        @self.processor('dirty_a')
        def invalidate_a(node_store, node):
            for a in self.name_to_nodes['a']:
                node_store.mark_node_dirty(a)

        self.processor('add_own_child', record)
        @self.processor('add_own_child')
        def add_own_child(node_store, node):
            node_store.insert_subtree(node, 0, CWDOMNode('a_child'))

        self.processor('wrap_self', record)
        @self.processor('wrap_self')
        def wrap_self(node_store, node):
            node_store.wrap_node(node, CWDOMNode('wrapper'))

        self.processor('wrap_a', record)
        @self.processor('wrap_a')
        def wrap_self(node_store, node):
            for a in self.name_to_nodes['a']:
                node_store.wrap_node(a, CWDOMNode('wrapper'))

        self.processor('replace_own_contents', record)
        @self.processor('replace_own_contents')
        def replace_own_contents(node_store, node):
            node_store.replace_subtree(node.children[0], CWDOMNode('contents'))

        self.processor('replace_self', record)
        @self.processor('replace_self')
        def replace_self(node_store, node):
            node_store.replace_node(node, CWDOMNode('replacement'))


class TestNodeStoreTraversals(CWTestCase):
    def test_postorder(self):
        ns = NodeStore(CWDOMRootNode([
            CWDOMDocumentNode('doc', [
                CWDOMNode('a'),
                CWDOMNode('b', [
                    CWDOMNode('x'),
                    CWDOMNode('y'),
                ]),
                CWDOMNode('c'),
            ])
        ]))
        self.assertEqual(
            [node.name for node in ns.postorder_traversal()],
            ['a', 'x', 'y', 'b', 'c', 'Document', 'Root'])
        self.assertEqual(
            [node.name for node in
             ns.postorder_traversal_allowing_ancestor_mutations()],
            ['a', 'x', 'y', 'b', 'c', 'Document', 'Root'])

    def test_postorder_2(self):
        header1 = CWDOMTagNode('h1', {}, [
            CWDOMTextNode('Header 1 text')
        ])
        header2 = CWDOMTagNode('h1', {}, [
            CWDOMTextNode('Header 2 text')
        ])
        ns = NodeStore(CWDOMRootNode([
            CWDOMDocumentNode('doc 1', [header1]),
            CWDOMDocumentNode('doc 2', [header2]),
        ]))
        self.assertEqual(
            [node.name for node in
             ns.postorder_traversal_allowing_ancestor_mutations()],
            ['Text', 'h1', 'Document', 'Text', 'h1', 'Document', 'Root'])

    def test_preorder(self):
        ns = NodeStore(CWDOMRootNode([
            CWDOMDocumentNode('doc', [
                CWDOMNode('a'),
                CWDOMNode('b', [
                    CWDOMNode('x'),
                    CWDOMNode('y'),
                ]),
                CWDOMNode('c'),
            ])
        ]))
        self.assertEqual(
            [node.name for node in ns.preorder_traversal()],
            ['Root', 'Document', 'a', 'b', 'x', 'y', 'c'])


class TestNodeStore(CWTestCase):
    def assertTreeIsConsistent(self, node):
        for child in node.children:
            self.assertEqual(child.get_parent(), node)
            self.assertTreeIsConsistent(child)

    def test_mark_dirty(self):
        ns = NodeStore(CWDOMRootNode([
            CWDOMDocumentNode('doc', [
                CWDOMNode('a'),
                CWDOMNode('b'),
                CWDOMNode('dirty_a')
            ])
        ]))
        library = LibraryForTesting()
        ns.apply_library(library)
        self.assertTreeIsConsistent(ns.root)
        self.assertEqual(library.visit_history, [
            'a', 'b', 'dirty_a', 'Document', 'Root', 'a'
        ])

    def test_get_is_descendant(self):
        a = CWDOMNode('a')
        root = CWDOMRootNode([a])
        ns = NodeStore(root)
        self.assertTrue(ns.get_is_descendant(a, root))
        self.assertFalse(ns.get_is_descendant(a, a))
        self.assertFalse(ns.get_is_descendant(root, a))

    def test_add_own_child(self):
        ns = NodeStore(CWDOMRootNode([
            CWDOMDocumentNode('doc', [
                CWDOMNode('a'),
                CWDOMNode('b'),
                CWDOMNode('add_own_child')
            ])
        ]))
        library = LibraryForTesting()
        ns.apply_library(library)
        self.assertTreeIsConsistent(ns.root)
        self.assertEqual(library.visit_history, [
            'a', 'b', 'add_own_child', 'Document', 'Root', 'a_child'])
        self.assertEqual(ns.root.get_string_for_test_comparison(), self.strip("""
            Root()
              Document(path='doc')
                a()
                b()
                add_own_child()
                  a_child()
        """))

    def test_add_root_child_fails(self):
        ns = NodeStore(CWDOMRootNode([
            CWDOMDocumentNode('doc', [
                CWDOMNode('a'),
                CWDOMNode('b'),
                CWDOMNode('add_root_child')
            ])
        ]))
        library = LibraryForTesting()
        @library.processor('add_root_child')
        def add_root_child(node_store, node):
            node_store.insert_subtree(node_store.root, 0, CWDOMNode('a_child'))
        with self.assertRaises(NodeStoreConsistencyError):
            ns.apply_library(library)

    def test_add_sibling_child_fails(self):
        a = CWDOMNode('a')
        ns = NodeStore(CWDOMRootNode([
            CWDOMDocumentNode('doc', [
                a,
                CWDOMNode('b'),
                TestNode('add_sibling_child')
            ])
        ]))
        library = LibraryForTesting()
        @library.processor('add_sibling_child')
        def add_root_child(node_store, node):
            node_store.insert_subtree(a, 0, CWDOMNode('a_child'))
        with self.assertRaises(NodeStoreConsistencyError):
            ns.apply_library(library)

    def test_wrap_self(self):
        ns = NodeStore(CWDOMRootNode([
            CWDOMDocumentNode('doc', [
                CWDOMNode('a'),
                CWDOMNode('b'),
                CWDOMNode('wrap_self')
            ])
        ]))
        library = LibraryForTesting()
        ns.apply_library(library)
        self.assertEqual(library.visit_history, [
            'a', 'b', 'wrap_self', 'wrapper', 'Document', 'Root'])
        self.assertEqual(ns.root.get_string_for_test_comparison(), self.strip("""
            Root()
              Document(path='doc')
                a()
                b()
                wrapper()
                  wrap_self()
        """))

    def test_wrap_child(self):
        ns = NodeStore(CWDOMRootNode([
            CWDOMDocumentNode('doc', [
                CWDOMNode('b'),
                CWDOMNode('wrap_a', [
                    CWDOMNode('a'),
                ])
            ])
        ]))
        library = LibraryForTesting()
        ns.apply_library(library)
        self.assertEqual(library.visit_history, [
            'b', 'a', 'wrap_a', 'Document', 'Root', 'wrapper'])
        self.assertEqual(ns.root.get_string_for_test_comparison(), self.strip("""
            Root()
              Document(path='doc')
                b()
                wrap_a()
                  wrapper()
                    a()
        """))

    def test_replace_own_contents(self):
        ns = NodeStore(CWDOMRootNode([
            CWDOMDocumentNode('doc', [
                CWDOMNode('replace_own_contents', [
                    CWDOMNode('a')
                ])
            ])
        ]))
        library = LibraryForTesting()
        ns.apply_library(library)
        self.assertEqual(library.visit_history, [
            'a', 'replace_own_contents', 'Document', 'Root', 'contents'])
        self.assertEqual(ns.root.get_string_for_test_comparison(), self.strip("""
            Root()
              Document(path='doc')
                replace_own_contents()
                  contents()
        """))

    def test_replace_self_contents(self):
        ns = NodeStore(CWDOMRootNode([
            CWDOMDocumentNode('doc', [
                CWDOMNode('replace_self', [
                    CWDOMNode('a')
                ])
            ])
        ]))
        library = LibraryForTesting()
        ns.apply_library(library)
        self.assertEqual(library.visit_history, [
            'a', 'replace_self', 'Document', 'Root', 'replacement'])
        self.assertEqual(ns.root.get_string_for_test_comparison(), self.strip("""
            Root()
              Document(path='doc')
                replacement()
                  a()
        """))

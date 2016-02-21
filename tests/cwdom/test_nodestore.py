import logging
import unittest
from collections import defaultdict
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


class TestLibrary(Library):
    def __init__(self):
        super().__init__()
        self.visit_history = []
        self.name_to_nodes = defaultdict(list)

        def record(node_store, node):
            self.visit_history.append(node.name)
            self.name_to_nodes[node.name].append(node)

        self.processor('Root', record)
        self.processor('Document', record)
        self.processor('a', record)
        self.processor('b', record)
        self.processor('a_child', record)
        self.processor('wrapper', record)

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

        self.end_processor(record)


class TestNodeStoreTraversals(unittest.TestCase):
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
            [node.name for node in ns.postorder_traversal_2()],
            ['a', 'x', 'y', 'b', 'c', 'Document', 'Root'])

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


class TestNodeStore(unittest.TestCase):
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
        library = TestLibrary()
        ns.apply_library(library)
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
        library = TestLibrary()
        ns.apply_library(library)
        self.assertEqual(library.visit_history, [
            'a', 'b', 'add_own_child', 'Document', 'Root', 'a_child'])
        self.assertEqual(ns.root.get_string_for_test_comparison(), strip("""
            Root()
              Document()
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
        library = TestLibrary()
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
        library = TestLibrary()
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
        library = TestLibrary()
        ns.apply_library(library)
        self.assertEqual(library.visit_history, [
            'a', 'b', 'wrap_self', 'wrapper', 'Document', 'Root'])
        self.assertEqual(ns.root.get_string_for_test_comparison(), strip("""
            Root()
              Document()
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
        library = TestLibrary()
        ns.apply_library(library)
        self.assertEqual(library.visit_history, [
            'b', 'a', 'wrap_a', 'Document', 'Root', 'wrapper'])
        self.assertEqual(ns.root.get_string_for_test_comparison(), strip("""
            Root()
              Document()
                b()
                wrap_a()
                  wrapper()
                    a()
        """))
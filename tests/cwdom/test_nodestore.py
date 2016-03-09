import logging
import unittest
from collections import defaultdict

from tests.CWTestCase import CWTestCase
from computerwords.cwdom.CWTree import CWTree, CWTreeConsistencyError
from computerwords.cwdom.nodes import *
from computerwords.library import Library


log = logging.getLogger(__name__)


class TestNode(CWNode):
    def __init__(self, name, **data):
        super().__init__(name)
        self.data = data


class LibraryForTesting(Library):
    def __init__(self):
        super().__init__()
        self.visit_history = []
        self.name_to_nodes = defaultdict(list)

        def record(tree, node):
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
        def invalidate_a(tree, node):
            for a in self.name_to_nodes['a']:
                tree.mark_node_dirty(a)

        self.processor('add_own_child', record)
        @self.processor('add_own_child')
        def add_own_child(tree, node):
            tree.insert_subtree(node, 0, CWNode('a_child'))

        self.processor('wrap_self', record)
        @self.processor('wrap_self')
        def wrap_self(tree, node):
            tree.wrap_node(node, CWNode('wrapper'))

        self.processor('wrap_a', record)
        @self.processor('wrap_a')
        def wrap_self(tree, node):
            for a in self.name_to_nodes['a']:
                tree.wrap_node(a, CWNode('wrapper'))

        self.processor('replace_own_contents', record)
        @self.processor('replace_own_contents')
        def replace_own_contents(tree, node):
            tree.replace_subtree(node.children[0], CWNode('contents'))

        self.processor('replace_self', record)
        @self.processor('replace_self')
        def replace_self(tree, node):
            tree.replace_node(node, CWNode('replacement'))

        self.processor('replace_self_subtree', record)
        @self.processor('replace_self_subtree')
        def replace_self_subtree(tree, node):
            tree.replace_subtree(node, CWNode('replacement', [
                CWNode('replacement')
            ]))


class TestCWTreeTraversals(CWTestCase):
    def test_postorder(self):
        tree = CWTree(CWRootNode([
            CWDocumentNode('doc', [
                CWNode('a'),
                CWNode('b', [
                    CWNode('x'),
                    CWNode('y'),
                ]),
                CWNode('c'),
            ])
        ]))
        self.assertEqual(
            [node.name for node in tree.postorder_traversal()],
            ['a', 'x', 'y', 'b', 'c', 'Document', 'Root'])
        self.assertEqual(
            [node.name for node in
             tree.postorder_traversal_allowing_ancestor_mutations()],
            ['a', 'x', 'y', 'b', 'c', 'Document', 'Root'])

    def test_postorder_2(self):
        header1 = CWTagNode('h1', {}, [
            CWTextNode('Header 1 text')
        ])
        header2 = CWTagNode('h1', {}, [
            CWTextNode('Header 2 text')
        ])
        tree = CWTree(CWRootNode([
            CWDocumentNode('doc 1', [header1]),
            CWDocumentNode('doc 2', [header2]),
        ]))
        self.assertEqual(
            [node.name for node in
             tree.postorder_traversal_allowing_ancestor_mutations()],
            ['Text', 'h1', 'Document', 'Text', 'h1', 'Document', 'Root'])

    def test_preorder(self):
        tree = CWTree(CWRootNode([
            CWDocumentNode('doc', [
                CWNode('a'),
                CWNode('b', [
                    CWNode('x'),
                    CWNode('y'),
                ]),
                CWNode('c'),
            ])
        ]))
        self.assertEqual(
            [node.name for node in tree.preorder_traversal()],
            ['Root', 'Document', 'a', 'b', 'x', 'y', 'c'])


class TestCWTree(CWTestCase):
    def assertTreeIsConsistent(self, node):
        for child in node.children:
            self.assertEqual(child.get_parent(), node)
            self.assertTreeIsConsistent(child)

    def test_mark_dirty(self):
        tree = CWTree(CWRootNode([
            CWDocumentNode('doc', [
                CWNode('a'),
                CWNode('b'),
                CWNode('dirty_a')
            ])
        ]))
        library = LibraryForTesting()
        tree.apply_library(library)
        self.assertTreeIsConsistent(tree.root)
        self.assertEqual(library.visit_history, [
            'a', 'b', 'dirty_a', 'Document', 'Root', 'a'
        ])

    def test_get_is_descendant(self):
        a = CWNode('a')
        root = CWRootNode([a])
        tree = CWTree(root)
        self.assertTrue(tree.get_is_descendant(a, root))
        self.assertFalse(tree.get_is_descendant(a, a))
        self.assertFalse(tree.get_is_descendant(root, a))

    def test_add_own_child(self):
        tree = CWTree(CWRootNode([
            CWDocumentNode('doc', [
                CWNode('a'),
                CWNode('b'),
                CWNode('add_own_child')
            ])
        ]))
        library = LibraryForTesting()
        tree.apply_library(library)
        self.assertTreeIsConsistent(tree.root)
        self.assertEqual(library.visit_history, [
            'a', 'b', 'add_own_child', 'Document', 'Root', 'a_child'])
        self.assertEqual(tree.root.get_string_for_test_comparison(), self.strip("""
            Root()
              Document(path='doc')
                a()
                b()
                add_own_child()
                  a_child()
        """))

    def test_add_root_child_fails(self):
        tree = CWTree(CWRootNode([
            CWDocumentNode('doc', [
                CWNode('a'),
                CWNode('b'),
                CWNode('add_root_child')
            ])
        ]))
        library = LibraryForTesting()
        @library.processor('add_root_child')
        def add_root_child(tree, node):
            tree.insert_subtree(tree.root, 0, CWNode('a_child'))
        with self.assertRaises(CWTreeConsistencyError):
            tree.apply_library(library)

    def test_add_sibling_child_fails(self):
        a = CWNode('a')
        tree = CWTree(CWRootNode([
            CWDocumentNode('doc', [
                a,
                CWNode('b'),
                TestNode('add_sibling_child')
            ])
        ]))
        library = LibraryForTesting()
        @library.processor('add_sibling_child')
        def add_root_child(tree, node):
            tree.insert_subtree(a, 0, CWNode('a_child'))
        with self.assertRaises(CWTreeConsistencyError):
            tree.apply_library(library)

    def test_wrap_self(self):
        tree = CWTree(CWRootNode([
            CWDocumentNode('doc', [
                CWNode('a'),
                CWNode('b'),
                CWNode('wrap_self')
            ])
        ]))
        library = LibraryForTesting()
        tree.apply_library(library)
        self.assertEqual(library.visit_history, [
            'a', 'b', 'wrap_self', 'wrapper', 'Document', 'Root'])
        self.assertEqual(tree.root.get_string_for_test_comparison(), self.strip("""
            Root()
              Document(path='doc')
                a()
                b()
                wrapper()
                  wrap_self()
        """))

    def test_wrap_child(self):
        tree = CWTree(CWRootNode([
            CWDocumentNode('doc', [
                CWNode('b'),
                CWNode('wrap_a', [
                    CWNode('a'),
                ])
            ])
        ]))
        library = LibraryForTesting()
        tree.apply_library(library)
        self.assertEqual(library.visit_history, [
            'b', 'a', 'wrap_a', 'Document', 'Root', 'wrapper'])
        self.assertEqual(tree.root.get_string_for_test_comparison(), self.strip("""
            Root()
              Document(path='doc')
                b()
                wrap_a()
                  wrapper()
                    a()
        """))

    def test_replace_own_contents(self):
        tree = CWTree(CWRootNode([
            CWDocumentNode('doc', [
                CWNode('replace_own_contents', [
                    CWNode('a')
                ])
            ])
        ]))
        library = LibraryForTesting()
        tree.apply_library(library)
        self.assertEqual(library.visit_history, [
            'a', 'replace_own_contents', 'Document', 'Root', 'contents'])
        self.assertEqual(tree.root.get_string_for_test_comparison(), self.strip("""
            Root()
              Document(path='doc')
                replace_own_contents()
                  contents()
        """))

    def test_replace_self(self):
        tree = CWTree(CWRootNode([
            CWDocumentNode('doc', [
                CWNode('replace_self', [
                    CWNode('a')
                ])
            ])
        ]))
        library = LibraryForTesting()
        tree.apply_library(library)
        self.assertEqual(library.visit_history, [
            'a', 'replace_self', 'Document', 'Root', 'replacement'])
        self.assertEqual(tree.root.get_string_for_test_comparison(), self.strip("""
            Root()
              Document(path='doc')
                replacement()
                  a()
        """))

    def test_replace_self_subtree(self):
        tree = CWTree(CWRootNode([
            CWDocumentNode('doc', [
                CWNode('replace_self_subtree', [
                    CWNode('a')
                ])
            ])
        ]))
        library = LibraryForTesting()
        tree.apply_library(library)
        self.assertEqual(library.visit_history, [
            'a', 'replace_self_subtree', 'Document', 'Root', 'replacement', 'replacement'])
        self.assertEqual(tree.root.get_string_for_test_comparison(), self.strip("""
            Root()
              Document(path='doc')
                replacement()
                  replacement()
        """))

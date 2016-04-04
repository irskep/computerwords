import unittest
import pathlib

from collections import OrderedDict

from computerwords.cwdom.nodes import CWDocumentNode
from computerwords.read_doc_tree import (
    read_doc_tree,
    DocTree,
    DocSubtree,
)


_empty = lambda subtree, doc_id, doc_path: []


def _print_doc_tree(doc_tree):
    for entry in doc_tree:
        _print_doc_subtree(entry)

def _print_doc_subtree(subtree, indent_level=0):
    print(' ' * indent_level + str(subtree.document_id))
    for child in subtree.children:
        _print_doc_subtree(child, indent_level + 2)


class ReadDocTreeTestCase(unittest.TestCase):
    def setUp(self):
        self.maxDiff = None
        self.path = pathlib.Path(__file__).resolve()
        self.test_dir = self.path.parent
        self.test_files_dir = self.test_dir / '_doc_tree_test_files'

        # keep lines short
        self.dir = self.test_files_dir

    def test_simple(self):
        doc_tree, _ = read_doc_tree(self.dir, ['index.md'], _empty)
        self.assertSequenceEqual(doc_tree.entries, [
            DocSubtree(self.dir / "index.md", ("index",), []),
        ])

    def test_flat(self):
        doc_tree, _ = read_doc_tree(
            self.dir, ['index.md', 'a.md'], _empty)
        self.assertSequenceEqual(doc_tree.entries, [
            DocSubtree(self.dir / "index.md", ("index",), []),
            DocSubtree(self.dir / "a.md", ('a',), []),
        ])

    def test_nested(self):
        doc_tree, _ = read_doc_tree(
            self.dir, [{'index.md': ['a.md']}], _empty)
        self.assertSequenceEqual(doc_tree.entries, [
            DocSubtree(self.dir / "index.md", ("index",), [
                DocSubtree(self.dir / "a.md", ('a',), []),
            ]),
        ])

    def test_double_nested(self):
        doc_tree, _ = read_doc_tree(
            self.dir, [{'index.md': [{'a.md': ['x/b.md']}]}], _empty)
        self.assertSequenceEqual(doc_tree.entries, [
            DocSubtree(self.dir / "index.md", ("index",), [
                DocSubtree(self.dir / "a.md", ('a',), [
                    DocSubtree(self.dir / "x" / "b.md", ('x', 'b'), []),
                ]),
            ]),
        ])

    def test_single_glob(self):
        doc_tree, _ = read_doc_tree(self.dir, ['x/*.md'], _empty)
        self.assertSequenceEqual(doc_tree.entries, [
            DocSubtree(self.dir / "x" / "b.md", ("x", "b"), []),
        ])

    def test_multi_glob(self):
        doc_tree, _ = read_doc_tree(self.dir, ['*.md'], _empty)
        self.assertSequenceEqual(doc_tree.entries, [
            DocSubtree(self.dir / "index.md", ("index",), []),
            DocSubtree(self.dir / "a.md", ('a',), []),
        ])

    def test_nested_glob(self):
        doc_tree, _ = read_doc_tree(self.dir, ['**/*.md'], _empty)
        self.assertSequenceEqual(doc_tree.entries, [
            DocSubtree(self.dir / "index.md", ("index",), []),
            DocSubtree(self.dir / "a.md", ('a',), []),
            DocSubtree(self.dir / "x" / "b.md", ("x", "b"), []),
            DocSubtree(self.dir / "y" / "index.md", ("y", "index"), []),
            DocSubtree(self.dir / "y" / "c.md", ("y", "c"), []),
            DocSubtree(self.dir / "y" / "yy" / "index.md", ("y", "yy", "index"), []),
            DocSubtree(self.dir / "y" / "yy" / "page2.md", ("y", "yy", "page2"), []),
            DocSubtree(self.dir / "y" / "yy" / "yyy" / "page3.md", ("y", "yy", "yyy", "page3"), []),
            DocSubtree(self.dir / "z" / "zz" / "blah.md", ("z", "zz", "blah"), []),
        ])

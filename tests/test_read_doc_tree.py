import unittest
import pathlib

from computerwords.cwdom.CWDOMNode import CWDOMDocumentNode
from computerwords.read_doc_tree import (
    read_doc_tree,
    DocTree,
    DocSubtree,
)


_empty = lambda subtree: []


def _print_doc_tree(doc_tree):
    for entry in doc_tree:
        _print_doc_subtree(entry)

def _print_doc_subtree(subtree, indent_level=0):
    print(' ' * indent_level + str(subtree.document_id))
    for child in subtree.children:
        _print_doc_subtree(child, indent_level + 2)


class ReadDocTreeTestCase(unittest.TestCase):
    def setUp(self):
        self.path = pathlib.Path(__file__).resolve()
        self.test_dir = self.path.parent
        self.test_files_dir = self.test_dir / '_doc_tree_test_files'

        # keep lines short
        self.dir = self.test_files_dir

    def test_simple(self):
        doc_tree, _ = read_doc_tree(self.dir, ['index.md'], _empty)
        self.assertSequenceEqual(doc_tree.entries, [
            DocSubtree(self.dir / "index.md", ("index.md",), []),
        ])

    def test_flat(self):
        doc_tree, _ = read_doc_tree(
            self.dir, ['index.md', 'a.md'], _empty)
        self.assertSequenceEqual(doc_tree.entries, [
            DocSubtree(self.dir / "index.md", ("index.md",), []),
            DocSubtree(self.dir / "a.md", ('a.md',), []),
        ])

    def test_nested(self):
        doc_tree, _ = read_doc_tree(
            self.dir, [{'index.md': ['a.md']}], _empty)
        self.assertSequenceEqual(doc_tree.entries, [
            DocSubtree(self.dir / "index.md", ("index.md",), [
                DocSubtree(self.dir / "a.md", ('a.md',), []),
            ]),
        ])

    def test_double_nested(self):
        doc_tree, _ = read_doc_tree(
            self.dir, [{'index.md': [{'a.md': ['x/b.md']}]}], _empty)
        self.assertSequenceEqual(doc_tree.entries, [
            DocSubtree(self.dir / "index.md", ("index.md",), [
                DocSubtree(self.dir / "a.md", ('a.md',), [
                    DocSubtree(self.dir / "x" / "b.md", ('x', 'b.md'), []),
                ]),
            ]),
        ])

    def test_single_glob(self):
        doc_tree, _ = read_doc_tree(self.dir, ['x/*.md'], _empty)
        self.assertSequenceEqual(doc_tree.entries, [
            DocSubtree(self.dir / "x" / "b.md", ("x", "b.md"), []),
        ])

    def test_multi_glob(self):
        doc_tree, _ = read_doc_tree(self.dir, ['*.md'], _empty)
        self.assertSequenceEqual(doc_tree.entries, [
            DocSubtree(self.dir / "index.md", ("index.md",), []),
            DocSubtree(self.dir / "a.md", ('a.md',), []),
        ])

    def test_nested_glob(self):
        doc_tree, _ = read_doc_tree(self.dir, ['**/*.md'], _empty)
        self.assertSequenceEqual(doc_tree.entries, [
            DocSubtree(self.dir / "a.md", ('a.md',), []),
            DocSubtree(self.dir / "index.md", ("index.md",), []),
            DocSubtree(self.dir / "x" / "b.md", ("x", "b.md"), []),
            DocSubtree(self.dir / "y" / "index.md", ("y", "index.md"), [
                DocSubtree(self.dir / "y" / "c.md", ("y", "c.md"), []),
            ]),
        ])

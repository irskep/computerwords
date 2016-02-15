import logging
import unittest

from computerwords.cwdom.NodeStore import NodeStore
from computerwords.cwdom.CWDOMNode import *
from computerwords.library import Library


log = logging.getLogger(__name__)


class TestLibrary(Library):
    def __init__(self):
        super().__init__()
        self.visit_history = []

        just_record = lambda node_store, node: self.record(node)
        def invalidate_a(node_store, node):
            for node in node_store.get_nodes('a'):
                node_store.invalidate(node)

        self.processor('Root', just_record)
        self.processor('Document', just_record)
        self.processor('a', just_record)
        self.processor('b', just_record)
        self.processor('c', just_record)
        self.processor('invalidate_a', just_record)
        self.processor('invalidate_a', invalidate_a)
        self.end_processor(just_record)

    def record(self, node):
        self.visit_history.append(node.name)


class TestNodeStore(unittest.TestCase):
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
            'Root', 'Document', 'a', 'b', 'c', CWDOMEndOfInputNode.NAME
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
            CWDOMEndOfInputNode.NAME, 'a'
        ])

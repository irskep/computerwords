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
        self.processor('Root', just_record)
        self.processor('Document', just_record)
        self.processor('a', just_record)
        self.processor('b', just_record)
        self.processor('c', just_record)
        self.end_processor(just_record)

    def record(self, node):
        self.visit_history.append(node.name)


class TestNodeStore(unittest.TestCase):
    def test_simple(self):
        logging.basicConfig(level=logging.DEBUG)

        # most tests won't need to build the tree this tedious way. this
        # particular test needs to verify the traversal key sort order.
        a = CWDOMTagNode('a', kwargs={})
        b = CWDOMTagNode('b', kwargs={})
        c = CWDOMTagNode('c', kwargs={})
        doc = CWDOMDocumentNode('doc')
        doc.set_children([a, b, c])
        root = CWDOMRootNode()
        root.set_children([doc])
        flat_nodes = [a, b, c, doc, root]

        ns = NodeStore(root)
        library = TestLibrary()
        ns.apply_library(library)
        self.assertEqual(library.visit_history, [
            'Root', 'Document', 'a', 'b', 'c', CWDOMEndOfInputNode.NAME
        ])

        reconstructed_pairs = sorted([
            (ns.get_traversal_key(n), n) for n in flat_nodes
        ])
        self.assertEqual(
            [pair[1] for pair in reconstructed_pairs],
            [root, doc, a, b, c])

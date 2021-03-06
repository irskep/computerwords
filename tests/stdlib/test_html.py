import unittest

from tests.CWTestCase import CWTestCase
from computerwords.cwdom.nodes import *
from computerwords.cwdom.CWTree import CWTree
from computerwords.library import Library
from computerwords.stdlib.basics import add_basics
from computerwords.stdlib.html import add_html


class LibraryForTesting(Library):
    def __init__(self):
        super().__init__()
        add_basics(self)
        add_html(self)

        self.visit_history = []
        def record(tree, node):
            self.visit_history.append(node.name)

        for tag in self.HTML_TAGS:
            self.processor(tag, record, before_others=True)
        for tag in self.ALIAS_HTML_TAGS:
            self.processor(tag, record, before_others=True)


class TestHTML(CWTestCase):
    def test_aliases(self):
        tree = CWTree(CWRootNode([
            CWDocumentNode('doc 1', [
                CWTagNode('strike', {}, []),
                CWTagNode('b', {}, []),
                CWTagNode('tt', {}, []),
            ]),
        ]))
        tree.apply_library(LibraryForTesting())
        self.assertEqual(tree.root.get_string_for_test_comparison(), self.strip("""
            Root()
              Document(path='doc 1')
                s(kwargs={})
                strong(kwargs={})
                code(kwargs={})
        """))

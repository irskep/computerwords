import unittest

from computerwords.cwdom.CWDOMNode import *
from computerwords.cwdom.NodeStore import NodeStore
from computerwords.library import Library
from computerwords.stdlib.basics import add_basics
from computerwords.stdlib.html import add_html
from computerwords.stdlib.links import add_links
from computerwords.stdlib.table_of_contents import (
    add_table_of_contents,
    TOCEntry,
)


library = Library()
add_basics(library)
add_html(library)
add_links(library)
add_table_of_contents(library)


class TestTableOfContents(unittest.TestCase):
    def test_collect_entries(self):
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
        ns.apply_library(library)
        self.assertEqual(header1.get_parent().data, {
            'toc_entry': TOCEntry(
                level=1, text='Header 1 text', ref_id='Header-1-text')
        })
        self.assertEqual(header2.get_parent().data, {
            'toc_entry': TOCEntry(
                level=1, text='Header 2 text', ref_id='Header-2-text')
        })

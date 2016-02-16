import logging
import unittest

from computerwords.cwdom.NodeStore import NodeStore, NodeStoreConsistencyError
from computerwords.cwdom.CWDOMNode import *
from computerwords.library import Library
from computerwords.stdlib.basics import add_basics
from computerwords.stdlib.table_of_contents import (
    add_table_of_contents,
    TOCEntry,
    _entries_to_nested_list,
)

from tests.CWTestCase import CWTestCase


log = logging.getLogger(__name__)


def get_library():
    library = Library()
    add_basics(library)
    add_table_of_contents(library)
    return library


class TestTOC(CWTestCase):
    def test_headers_add_data(self):
        ns = NodeStore(CWDOMRootNode([
            CWDOMDocumentNode('doc', [
                CWDOMTagNode('h1', {}, [CWDOMTextNode('Heading 1')])
            ])
        ]))
        ns.apply_library(get_library())
        d = ns.processor_data
        self.assertIsNone(d['toc_entry_to_number'])
        self.assertTrue(d['toc_entries_is_complete'])
        self.assertEqual(d['toc_entries'], [
            TOCEntry(0, 'doc', 'doc'),
            TOCEntry(1, 'Heading 1', 'Heading-1')
        ])

    def test_entries_to_nested_list(self):
        entries = [
            TOCEntry(0, "doc", "doc"),
            TOCEntry(1, "A header", "A-header"),
            TOCEntry(2, "subsection", "subsection"),
            TOCEntry(1, "Another header", "Another-header"),
            TOCEntry(3, "subsubsection", "subsubsection"),
            TOCEntry(0, "anotherdoc", "anotherdoc"),
            TOCEntry(3, "asdf", "asdf"),
        ]
        self.assertEqual(_entries_to_nested_list(entries), [
            (TOCEntry(0, 'doc', 'doc'), [
                (TOCEntry(1, "A header", "A-header"), [
                    (TOCEntry(2, "subsection", "subsection"), [])
                ]),
                (TOCEntry(1, "Another header", "Another-header"), [
                    (TOCEntry(3, "subsubsection", "subsubsection"), [])
                ]),
            ]),
            (TOCEntry(0, 'anotherdoc', 'anotherdoc'), [
                (TOCEntry(3, "asdf", "asdf"), [])
            ]),
        ])

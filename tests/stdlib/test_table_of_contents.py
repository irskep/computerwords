import unittest

from tests.CWTestCase import CWTestCase
from computerwords.cwdom.CWDOMNode import *
from computerwords.cwdom.NodeStore import NodeStore
from computerwords.library import Library
from computerwords.stdlib.basics import add_basics
from computerwords.stdlib.html import add_html
from computerwords.stdlib.links import add_links
from computerwords.stdlib.table_of_contents import (
    add_table_of_contents,
    TOCEntry,
    _entries_to_nested_list,
)


library = Library()
add_basics(library)
add_html(library)
add_links(library)
add_table_of_contents(library)


class TestTableOfContents(CWTestCase):
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
                level=1, heading_node=header1, ref_id='Header-1-text')
        })
        self.assertEqual(header2.get_parent().data, {
            'toc_entry': TOCEntry(
                level=1, heading_node=header2, ref_id='Header-2-text')
        })

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

    def test_make_toc(self):
        ns = NodeStore(CWDOMRootNode([
            CWDOMDocumentNode('doc 1', [
                CWDOMTagNode('table_of_contents', {}, []),
                CWDOMTagNode('h1', {}, [
                    CWDOMTextNode('Header 1 text')
                ]),
                CWDOMTagNode('h2', {}, [
                    CWDOMTextNode('Subheader 1 text')
                ]),
            ]),
            CWDOMDocumentNode('doc 2', [
                CWDOMTagNode('h1', {}, [
                    CWDOMTextNode('Header 2 text')
                ]),
            ]),
        ]))
        ns.apply_library(library)
        self.assertEqual(ns.root.get_string_for_test_comparison(), self.strip("""
            Root()
              Document(path='doc 1')
                ol(kwargs={'class': 'table-of-contents'})
                  li(kwargs={})
                    Link(ref_id='Header-1-text')
                      h1(kwargs={})
                        'Header 1 text'
                    ol(kwargs={})
                      li(kwargs={})
                        Link(ref_id='Subheader-1-text')
                          h2(kwargs={})
                            'Subheader 1 text'
                  li(kwargs={})
                    Link(ref_id='Header-2-text')
                      h1(kwargs={})
                        'Header 2 text'
                Anchor(ref_id='Header-1-text')
                  h1(kwargs={})
                    'Header 1 text'
                Anchor(ref_id='Subheader-1-text')
                  h2(kwargs={})
                    'Subheader 1 text'
              Document(path='doc 2')
                Anchor(ref_id='Header-2-text')
                  h1(kwargs={})
                    'Header 2 text'
        """))

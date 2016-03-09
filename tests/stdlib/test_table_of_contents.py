import unittest

from tests.CWTestCase import CWTestCase
from computerwords.cwdom.nodes import *
from computerwords.cwdom.CWTree import CWTree
from computerwords.library import Library
from computerwords.stdlib.basics import add_basics
from computerwords.stdlib.html import add_html
from computerwords.stdlib.links import add_links
from computerwords.stdlib.table_of_contents import (
    add_table_of_contents,
    TOCEntry,
    _entries_to_nested_list,
)


class TableOfContentsTestCase(CWTestCase):
    def setUp(self):
        super().setUp()
        self.library = Library()
        add_basics(self.library)
        add_html(self.library)
        add_links(self.library)
        add_table_of_contents(self.library)

    def test_collect_entries(self):
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
        tree.apply_library(self.library)
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
            TOCEntry(2, "subsection 2", "subsection-2"),
            TOCEntry(1, "Another header", "Another-header"),
            TOCEntry(3, "subsubsection", "subsubsection"),
            TOCEntry(0, "anotherdoc", "anotherdoc"),
            TOCEntry(3, "asdf", "asdf"),
        ]
        self.assertEqual(_entries_to_nested_list(entries), [
            (TOCEntry(0, 'doc', 'doc'), [
                (TOCEntry(1, "A header", "A-header"), [
                    (TOCEntry(2, "subsection", "subsection"), []),
                    (TOCEntry(2, "subsection 2", "subsection-2"), []),
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
        tree = CWTree(CWRootNode([
            CWDocumentNode('doc 1', [
                CWTagNode('table-of-contents', {}, []),
                CWTagNode('h1', {}, [
                    CWTextNode('Header 1 text')
                ]),
                CWTagNode('h2', {}, [
                    CWTextNode('Subheader 1 text')
                ]),
                CWTagNode('h2', {}, [
                    CWTextNode('Subheader 2 text')
                ]),
            ]),
            CWDocumentNode('doc 2', [
                CWTagNode('h1', {}, [
                    CWTextNode('Header 2 text')
                ]),
            ]),
        ]))
        tree.apply_library(self.library)
        self.assertEqual(tree.root.get_string_for_test_comparison(), self.strip("""
            Root()
              Document(path='doc 1')
                nav(kwargs={'class': 'table-of-contents'})
                  ol(kwargs={})
                    li(kwargs={})
                      Link(ref_id='Header-1-text')
                        'Header 1 text'
                      ol(kwargs={})
                        li(kwargs={})
                          Link(ref_id='Subheader-1-text')
                            'Subheader 1 text'
                        li(kwargs={})
                          Link(ref_id='Subheader-2-text')
                            'Subheader 2 text'
                    li(kwargs={})
                      Link(ref_id='Header-2-text')
                        'Header 2 text'
                Anchor(ref_id='Header-1-text', kwargs={'class': 'header-anchor'})
                  h1(kwargs={})
                    'Header 1 text'
                Anchor(ref_id='Subheader-1-text', kwargs={'class': 'header-anchor'})
                  h2(kwargs={})
                    'Subheader 1 text'
                Anchor(ref_id='Subheader-2-text', kwargs={'class': 'header-anchor'})
                  h2(kwargs={})
                    'Subheader 2 text'
              Document(path='doc 2')
                Anchor(ref_id='Header-2-text', kwargs={'class': 'header-anchor'})
                  h1(kwargs={})
                    'Header 2 text'
        """))

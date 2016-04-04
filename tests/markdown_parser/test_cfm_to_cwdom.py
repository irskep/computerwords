import unittest

from computerwords.cwdom.nodes import *
from computerwords.markdown_parser import CFMParserConfig
from computerwords.markdown_parser.cfm_to_cwdom import cfm_to_cwdom

from tests.CWTestCase import CWTestCase


DOC_ID = ('test.md',)
DOC_PATH = 'test.md'


TAGS = {'a', 'b', 'c', 'x', 'y', 'z'}
CONFIG = CFMParserConfig(
    document_id=DOC_ID, document_path=DOC_PATH, allowed_tags=TAGS)


class IntegratedHTMLParsingTestCase(CWTestCase):
    def test_inline_html(self):
        root = CWRootNode(cfm_to_cwdom("a <b><c>b</c></b> c", CONFIG))
        self.assertMultiLineEqual(
            root.get_string_for_test_comparison(), self.strip("""
                Root()
                  'a '
                  b(kwargs={})
                    c(kwargs={})
                      'b'
                  ' c'
            """))

    def test_self_closing_tag(self):
        root = CWRootNode(cfm_to_cwdom("<a />", CONFIG))
        self.assertMultiLineEqual(
            root.get_string_for_test_comparison(), self.strip("""
                Root()
                  a(kwargs={})
            """))

    def test_block_html_1(self):
        s = self.strip("""
            <x>some test
            </x>abc

            par
        """)
        root = CWRootNode(cfm_to_cwdom(s, CONFIG))
        self.assertMultiLineEqual(
            root.get_string_for_test_comparison(), self.strip("""
                Root()
                  p(kwargs={})
                    x(kwargs={})
                      'some test'
                      ' '
                    'abc'
                  p(kwargs={})
                    'par'
            """))

    @unittest.skip("")
    def test_block_html_2(self):
        s = self.strip("""
            abc<x>some <x>test

            </x>

            </x>abc
        """)
        print('----------------------')
        self.log_node(CWRootNode(cfm_to_cwdom(s, CONFIG, fix_tags=False)))
        root = CWRootNode(cfm_to_cwdom(s, CONFIG))
        self.log_node(root)
        self.assertMultiLineEqual(
            root.get_string_for_test_comparison(), self.strip("""
                Root()
                  p(kwargs={})
                    'abc'
                  x(kwargs={})
                    p(kwargs={})
                      'some test'
                  p(kwargs={})
                    'abc'
            """))
        print('^^^^^')

    @unittest.skip("")
    def test_block_html_3(self):
        s = self.strip("""
            <x>

            some test</x>
        """)
        root = CWRootNode(cfm_to_cwdom(s, CONFIG))
        self.log_node(root)

    def test_block_html_4(self):
        s = self.strip("""
            <x>
            some test
            </x>
        """)
        root = CWRootNode(cfm_to_cwdom(s, CONFIG))
        self.assertMultiLineEqual(
            root.get_string_for_test_comparison(), self.strip("""
                Root()
                  x(kwargs={})
                    'some test'
            """))

    def test_block_html_5(self):
        s = self.strip("""
            <x>
            some test

            </x>
        """)
        root = CWRootNode(cfm_to_cwdom(s, CONFIG))
        self.assertMultiLineEqual(
            root.get_string_for_test_comparison(), self.strip("""
                Root()
                  x(kwargs={})
                    '\\nsome test'
            """))

    @unittest.skip("")
    def test_block_html_6(self):
        s = self.strip("""
            <x>

            some test
            </x>
        """)
        self.log_node(CWRootNode(cfm_to_cwdom(s, CONFIG, fix_tags=False)))
        root = CWRootNode(cfm_to_cwdom(s, CONFIG))
        self.assertMultiLineEqual(
            root.get_string_for_test_comparison(), self.strip("""
                Root()
                  x(kwargs={})
                    p(kwargs={})
                      'some test'
            """))

    def test_block_html_7(self):
        s = self.strip("""
            <x>

            some test

            </x>
        """)
        root = CWRootNode(cfm_to_cwdom(s, CONFIG))
        self.assertMultiLineEqual(
            root.get_string_for_test_comparison(), self.strip("""
                Root()
                  x(kwargs={})
                    p(kwargs={})
                      'some test'
            """))

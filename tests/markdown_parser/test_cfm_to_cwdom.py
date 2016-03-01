import unittest

from computerwords.cwdom.CWDOMNode import *
from computerwords.markdown_parser.cfm_to_cwdom import cfm_to_cwdom

from tests.CWTestCase import CWTestCase


TAGS = {'a', 'b', 'c', 'x', 'y', 'z'}


class IntegratedHTMLParsingTestCase(CWTestCase):
    def test_inline_html(self):
        root = CWDOMRootNode(cfm_to_cwdom("a <b>b</b> c", TAGS))
        self.assertSequenceEqual(
            root.get_string_for_test_comparison(), self.strip("""
                Root()
                  'a '
                  b(kwargs={})
                    'b'
                  ' c'
            """)
        )

    @unittest.skip("")
    def test_block_html_1(self):
        s = self.strip("""
            <x>some test
            </x>
        """)
        root = CWDOMRootNode(cfm_to_cwdom(s, TAGS))
        self.log_node(root)

    @unittest.skip("")
    def test_block_html_2(self):
        s = self.strip("""
            <x>some test

            </x>
        """)
        root = CWDOMRootNode(cfm_to_cwdom(s, TAGS))
        self.log_node(root)

    @unittest.skip("")
    def test_block_html_3(self):
        s = self.strip("""
            <x>

            some test</x>
        """)
        root = CWDOMRootNode(cfm_to_cwdom(s, TAGS))
        self.log_node(root)

    @unittest.skip("")
    def test_block_html_4(self):
        s = self.strip("""
            <x>
            some test
            </x>
        """)
        root = CWDOMRootNode(cfm_to_cwdom(s, TAGS))
        self.log_node(root)

    @unittest.skip("")
    def test_block_html_5(self):
        s = self.strip("""
            <x>
            some test

            </x>
        """)
        root = CWDOMRootNode(cfm_to_cwdom(s, TAGS))
        self.log_node(root)

    @unittest.skip("")
    def test_block_html_6(self):
        s = self.strip("""
            <x>

            some test
            </x>
        """)

    @unittest.skip("")
    def test_block_html_7(self):
        s = self.strip("""
            <x>

            some test

            </x>
        """)
        root = CWDOMRootNode(cfm_to_cwdom(s, TAGS))
        self.log_node(root)

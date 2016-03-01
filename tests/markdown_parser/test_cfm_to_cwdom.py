from computerwords.cwdom.CWDOMNode import *
from computerwords.markdown_parser.cfm_to_cwdom import cfm_to_cwdom

from tests.CWTestCase import CWTestCase


TAGS = {'a', 'b', 'c'}


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

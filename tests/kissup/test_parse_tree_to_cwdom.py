import unittest
from tests.CWTestCase import CWTestCase
from computerwords.markdown_parser.parse_tree_to_cwdom import (
    parse_tree_to_cwdom,
    DuplicateArgumentsError,
)
from computerwords.markdown_parser import CFMParserConfig
from computerwords.markdown_parser.cfm_to_cwdom import lex_and_parse_html
from computerwords.cwdom.nodes import CWDocumentNode
from computerwords.cwdom.CWTree import CWTree


DOC_ID = ('test.md',)
DOC_PATH = 'test.md'


class TestParseTreeToCW(CWTestCase):
    def test_basic(self):
        parse_tree = lex_and_parse_html(
            "outer text <abc x=y>inner text</abc>",
            config=CFMParserConfig(
                document_id=DOC_ID, document_path=DOC_PATH,
                allowed_tags={'abc'}))
        tree = CWTree(CWDocumentNode('test.md', parse_tree_to_cwdom(parse_tree)))

        self.assertEqual(tree.root.get_string_for_test_comparison(), self.strip("""
            Document(path='test.md')
              'outer text '
              abc(kwargs={'x': 'y'})
                'inner text'
        """))

    def test_duplicate_arg(self):
        with self.assertRaises(DuplicateArgumentsError):
            parse_tree = lex_and_parse_html(
                "outer text <abc x=y x=z>inner text</abc>",
                config=CFMParserConfig(
                    document_id=DOC_ID, document_path=DOC_PATH,
                    allowed_tags={'abc'}))
            dom = parse_tree_to_cwdom(parse_tree)


if __name__ == '__main__':
    unittest.main()

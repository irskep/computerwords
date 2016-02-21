import unittest
from tests.CWTestCase import CWTestCase
from computerwords.kissup.parse_tree_to_cwdom import (
    parse_tree_to_cwdom,
    DuplicateArgumentsError,
)
from computerwords.kissup import lex_and_parse_kissup
import computerwords.cwdom.CWDOMNode as DOM
from computerwords.cwdom.NodeStore import NodeStore


class TestParseTreeToCWDOM(CWTestCase):
    def test_basic(self):
        parse_tree = lex_and_parse_kissup(
            "outer text [abc x=y]inner text[/abc]", allowed_tags={'abc'})
        ns = parse_tree_to_cwdom(parse_tree)

        self.assertEqual(ns.root.get_string_for_test_comparison(), self.strip("""
            Root()
              Document(path='stdin.bb')
                'outer text '
                abc(kwargs={'x': 'y'})
                  'inner text'
        """))

    def test_duplicate_arg(self):
        with self.assertRaises(DuplicateArgumentsError):
            parse_tree = lex_and_parse_kissup(
                "outer text [abc x=y x=z]inner text[/abc]",
                allowed_tags={'abc'})
            dom = parse_tree_to_cwdom(parse_tree)


if __name__ == '__main__':
    unittest.main()

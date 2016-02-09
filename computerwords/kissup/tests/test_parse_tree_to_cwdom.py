import unittest
from computerwords.kissup.parse_tree_to_cwdom import (
    parse_tree_to_cwdom,
    DuplicateArgumentsError,
)
from computerwords.kissup import lex_and_parse_kissup
import computerwords.cwdom as DOM


class TestParseTreeToCWDOM(unittest.TestCase):
    def test_basic(self):
        parse_tree = lex_and_parse_kissup(
            "outer text [abc x=y]inner text[/abc]", allowed_tags={'abc'})
        dom = parse_tree_to_cwdom(parse_tree)
        self.assertEqual(dom, DOM.NodeStore(DOM.CWDOMRootNode([
            DOM.CWDOMTextNode('outer text '),
            DOM.CWDOMTagNode('abc', {'x': 'y'}, [
                DOM.CWDOMTextNode('inner text'),
            ])
        ])))

    def test_duplicate_arg(self):
        with self.assertRaises(DuplicateArgumentsError):
            parse_tree = lex_and_parse_kissup(
                "outer text [abc x=y x=z]inner text[/abc]",
                allowed_tags={'abc'})
            dom = parse_tree_to_cwdom(parse_tree)


if __name__ == '__main__':
    unittest.main()

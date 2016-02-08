import unittest
from kissup.parse_tree_to_cwdom import parse_tree_to_cwdom
from kissup import lex_and_parse_kissup


class TestParseTreeToCWDOM(unittest.TestCase):
    def test_basic(self):
        parse_tree = lex_and_parse_kissup(
            "outer text [abc]inner text[/abc]", allowed_tags={'abc'}
            )
        dom = parse_tree_to_cwdom(parse_tree)


if __name__ == '__main__':
    unittest.main()
import unittest
from kissup.parse_tree_to_cwdom import parse_tree_to_cwdom, DuplicateArgumentsError
from kissup import lex_and_parse_kissup


class TestParseTreeToCWDOM(unittest.TestCase):
    def test_basic(self):
        parse_tree = lex_and_parse_kissup(
            "outer text [abc x=y]inner text[/abc]", allowed_tags={'abc'}
            )
        dom = parse_tree_to_cwdom(parse_tree)
        print(repr(dom))

    def test_duplicate_arg(self):
        with self.assertRaises(DuplicateArgumentsError):
            parse_tree = lex_and_parse_kissup(
                "outer text [abc x=y x=z]inner text[/abc]",
                allowed_tags={'abc'})
            dom = parse_tree_to_cwdom(parse_tree)


if __name__ == '__main__':
    unittest.main()
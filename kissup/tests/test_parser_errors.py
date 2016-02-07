import unittest
from textwrap import dedent

from kissup import lexer
from kissup import parser


def lex(s):
    return list(lexer.lex_kissup(s))


def strip(s):
    return dedent(s)[1:-1]


class TestParseErrors(unittest.TestCase):

    def test_trailing_garbage(self):
        tokens = lex('text[abc /][')
        with self.assertRaisesRegex(
                parser.ParseError,
                r"Line 0 col 11: Unable to parse token \["):
            parser.parse_kissup(tokens)

    def test_mismatched_tags(self):
        tokens = lex('[abc]inner[/xyz]')
        with self.assertRaises(parser.ParseError):
            parser.parse_kissup(tokens)


if __name__ == '__main__':
    unittest.main()

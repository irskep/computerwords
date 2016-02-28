import unittest
from textwrap import dedent

from computerwords.markdown_parser.html_lexer import lex_html
from computerwords.markdown_parser import html_parser


def lex(s):
    return list(lex_html(s))


def strip(s):
    return dedent(s)[1:-1]


class TestParseErrors(unittest.TestCase):

    def test_trailing_garbage(self):
        tokens = lex('text<abc /><')
        with self.assertRaisesRegex(
                html_parser.ParseError,
                r"Line 0 col 11: Unable to parse token \<"):
            html_parser.parse_html(tokens, allowed_tags={'abc'})

    def test_mismatched_tags(self):
        tokens = lex('<abc>inner</xyz>')
        msg_re = r"Line 0 col 1: Tag mismatch: abc \(line 0, col 1\) and xyz \(line 0, col 12\). Did you forget to close your \<abc\> tag\?"
        with self.assertRaisesRegex(html_parser.TagMismatchError, msg_re):
            html_parser.parse_html(tokens, allowed_tags={'abc', 'xyz'})

    def test_disallowed_tags_1(self):
        tokens = lex('text <foo></foo>')
        msg_re = r"Line 0 col 6: Unknown tag: foo"
        with self.assertRaisesRegex(html_parser.UnknownTagError, msg_re):
            html_parser.parse_html(tokens, allowed_tags={'abc', 'xyz'})

    def test_disallowed_tags_2(self):
        tokens = lex('text <foo />')
        msg_re = r"Line 0 col 6: Unknown tag: foo"
        with self.assertRaisesRegex(html_parser.UnknownTagError, msg_re):
            html_parser.parse_html(tokens, allowed_tags={'abc', 'xyz'})


if __name__ == '__main__':
    unittest.main()

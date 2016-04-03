import unittest
from textwrap import dedent

from computerwords.markdown_parser import html_parser, CFMParserConfig
from computerwords.markdown_parser.html_lexer import lex_html


DOC_ID = ('test.md',)
DOC_PATH = 'test.md'


def lex(s):
    return list(lex_html(s))


def strip(s):
    return dedent(s)[1:-1]


class TestParseErrors(unittest.TestCase):

    def test_trailing_garbage(self):
        tokens = lex('text<abc /><')
        config = CFMParserConfig(document_id=DOC_ID, allowed_tags={'abc'})
        with self.assertRaisesRegex(
                html_parser.ParseError,
                r"Line 0 col 11: Unable to parse token \<"):
            html_parser.parse_html(tokens, config=config)

    def test_mismatched_tags(self):
        tokens = lex('<abc>inner</xyz>')
        msg_re = r"Line 0 col 1: Tag mismatch: abc \(line 0, col 1\) and xyz \(line 0, col 12\). Did you forget to close your \<abc\> tag\?"
        config = CFMParserConfig(document_id=DOC_ID, allowed_tags={'abc', 'xyz'})
        with self.assertRaisesRegex(html_parser.TagMismatchError, msg_re):
            html_parser.parse_html(tokens, config=config)

    def test_disallowed_tags_1(self):
        tokens = lex('text <foo></foo>')
        msg_re = r"Line 0 col 6: Unknown tag: foo"
        config = CFMParserConfig(document_id=DOC_ID, allowed_tags={'abc', 'xyz'})
        with self.assertRaisesRegex(html_parser.UnknownTagError, msg_re):
            html_parser.parse_html(tokens, config=config)

    def test_disallowed_tags_2(self):
        tokens = lex('text <foo />')
        msg_re = r"Line 0 col 6: Unknown tag: foo"
        config = CFMParserConfig(document_id=DOC_ID, allowed_tags={'abc', 'xyz'})
        with self.assertRaisesRegex(html_parser.UnknownTagError, msg_re):
            html_parser.parse_html(tokens, config=config)


if __name__ == '__main__':
    unittest.main()

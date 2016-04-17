import unittest
from textwrap import dedent

from computerwords.markdown_parser import html_parser, CFMParserConfig
from computerwords.markdown_parser.html_lexer import lex_html


DOC_ID = ('test.md',)
DOC_PATH = 'test.md'


def get_config(allowed_tags):
    return CFMParserConfig(
        document_id=DOC_ID, document_path=DOC_PATH, allowed_tags=allowed_tags)


def lex(config, s):
    return list(lex_html(config, s))


def strip(s):
    return dedent(s)[1:-1]


class TestParseErrors(unittest.TestCase):

    def test_trailing_garbage(self):
        config = get_config({'abc'})
        tokens = lex(config, 'text<abc /><')
        with self.assertRaises(
                html_parser.ParseError,
                msg="1:12-13: Unable to parse token <"):
            html_parser.parse_html(tokens, config=config)

    def test_mismatched_tags(self):
        config = get_config({'abc', 'xyz'})
        tokens = lex(config, '<abc>inner</xyz>')
        msg = (
            "'test.md':1:2-16: Tag mismatch: " +
            "abc (0:1-4) and xyz (0:12-15). " +
            "Did you forget to close your <abc> tag?")
        with self.assertRaises(html_parser.TagMismatchError, msg=msg):
            html_parser.parse_html(tokens, config=config)

    def test_disallowed_tags_1(self):
        config = get_config({'abc', 'xyz'})
        tokens = lex(config, 'text <foo></foo>')
        msg = "'test.md':1:7-10: Unknown tag: foo"
        with self.assertRaises(html_parser.UnknownTagError, msg=msg):
            html_parser.parse_html(tokens, config=config)

    def test_disallowed_tags_2(self):
        config = get_config({'abc', 'xyz'})
        tokens = lex(config, 'text <foo />')
        msg = "'test.md':1:7-10: Unknown tag: foo"
        with self.assertRaisesRegex(html_parser.UnknownTagError, msg):
            html_parser.parse_html(tokens, config=config)


if __name__ == '__main__':
    unittest.main()

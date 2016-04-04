import unittest
from textwrap import dedent

from computerwords.markdown_parser import CFMParserConfig
from computerwords.markdown_parser import html_lexer
from computerwords.markdown_parser import tokens as t
from computerwords.markdown_parser import ast
from computerwords.markdown_parser import parser_support
from computerwords.markdown_parser.src_loc import (
    SourceLocation as L,
    SourceRange as R,
)


parse_funcs = parser_support.PARSE_FUNC_REGISTRY


def lex(s):
    config = CFMParserConfig(
        document_id=('test.md',), document_path='test.md', allowed_tags=set())
    return list(html_lexer.lex_html(config, s))


def strip(s):
    return dedent(s)[1:-1]


class TestLexer(unittest.TestCase):
    def test_simple(self):
        self.assertEqual(lex('<'), [
            t.BracketLeftToken( L(0, 0, 0).plus(1)),
            t.EndToken(         L(0, 1, 1).plus(0)),
        ])
        self.assertEqual(lex('a'), [
            t.TextToken(        L(0, 0, 0).plus(1), 'a'),
            t.EndToken(         L(0, 1, 1).plus(0)),
        ])
        self.assertEqual(lex('a<'), [
            t.TextToken(        L(0, 0, 0).plus(1), 'a'),
            t.BracketLeftToken( L(0, 1, 1).plus(1), '<'),
            t.EndToken(         L(0, 2, 2).plus(0)),
        ])

    def test_text_good_escapes(self):
        input_str = r'abcd\\ fooey \[ \] \< \>'
        expected_output_str = r'abcd\ fooey [ ] < >'
        self.assertEqual(lex(input_str), [
            t.TextToken(L(0, 0, 0).plus(len(input_str)), expected_output_str),
            # End token comes at the end of the *input* string!
            t.EndToken(L(0, len(input_str), len(input_str)).plus(0)),
        ])

    def test_text_bad_escapes(self):
        expected = "0:0: A backslash in text must be followed by one of: ['<', '>', '[', '\\', ']']"
        with self.assertRaises(html_lexer.LexError, msg=expected) as e:
            lex(r'\z')
        with self.assertRaises(html_lexer.LexError):
            lex("\\")

    def test_stuff_that_fails_outside_brackets(self):
        with self.assertRaises(html_lexer.LexError):
            lex('>')

    def test_bbcode_simple(self):
        tokens = lex("<aa  bb=cc>text</aa>")
        self.assertSequenceEqual(tokens, [
            t.BracketLeftToken( L(0, 0, 0).plus(1)),
            t.BBWordToken(      L(0, 1, 1).plus(2), 'aa'),
            t.SpaceToken(       L(0, 3, 3).plus(2), '  '),
            t.BBWordToken(      L(0, 5, 5).plus(2), 'bb'),
            t.EqualsToken(      L(0, 7, 7).plus(1)),
            t.BBWordToken(      L(0, 8, 8).plus(2), 'cc'),
            t.BracketRightToken(L(0, 10, 10).plus(1)),
            t.TextToken(        L(0, 11, 11).plus(4), 'text'),
            t.BracketLeftToken( L(0, 15, 15).plus(1)),
            t.SlashToken(       L(0, 16, 16).plus(1)),
            t.BBWordToken(      L(0, 17, 17).plus(2), 'aa'),
            t.BracketRightToken(L(0, 19, 19).plus(1)),
            t.EndToken(         L(0, 20, 20).plus(0)),
        ])

    def test_bbcode_with_string_literals(self):
        input_string = r'<"escaped \"\\[] string" />' 
        tokens = lex(input_string)
        self.assertEqual(tokens, [
            t.BracketLeftToken( L(0, 0, 0).plus(1)),
            t.StringToken(      L(0, 1, 1).plus(23), r'escaped "\[] string'),
            t.SpaceToken(       L(0, 24, 24).plus(1), ' '),
            t.SlashToken(       L(0, 25, 25).plus(1)),
            t.BracketRightToken(L(0, 26, 26).plus(1)),
            t.EndToken(         L(0, 27, 27).plus(0)),
        ])

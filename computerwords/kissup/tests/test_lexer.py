import unittest
from textwrap import dedent

from computerwords.kissup import lexer
from computerwords.kissup import tokens as t
from computerwords.kissup import ast
from computerwords.kissup import parser
from computerwords.kissup import parser_support


parse_funcs = parser_support.PARSE_FUNC_REGISTRY


def lex(s):
    return list(lexer.lex_kissup(s))


def strip(s):
    return dedent(s)[1:-1]


class TestLexer(unittest.TestCase):
    def test_simple(self):
        self.assertEqual(lex('['), [
            t.BracketLeftToken(0, 0),
            t.EndToken(0, 1)
        ])
        self.assertEqual(lex('a'), [
            t.TextToken(0, 0, 'a'),
            t.EndToken(0, 1)
        ])
        self.assertEqual(lex('a['), [
            t.TextToken(0, 0, 'a'),
            t.BracketLeftToken(0, 1, '['),
            t.EndToken(0, 2)
        ])

    def test_text_good_escapes(self):
        input_str = r'abcd\\ fooey \[ \]'
        expected_output_str = r'abcd\ fooey [ ]'
        self.assertEqual(lex(input_str), [
            t.TextToken(0, 0, expected_output_str),
            # End token comes at the end of the *input* string!
            t.EndToken(0, len(input_str))
        ])

    def test_text_bad_escapes(self):
        with self.assertRaises(lexer.LexError):
            lex(r'\z')
        with self.assertRaises(lexer.LexError):
            lex("\\")

    def test_stuff_that_fails_outside_brackets(self):
        with self.assertRaises(lexer.LexError):
            lex(']')

    def test_bbcode_simple(self):
        tokens = lex("[aa  bb=cc]text[/aa]")
        self.assertEqual(tokens, [
            t.BracketLeftToken(0, 0),
            t.BBWordToken(0, 1, 'aa'),
            t.SpaceToken(0, 3, '  '),
            t.BBWordToken(0, 5, 'bb'),
            t.EqualsToken(0, 7),
            t.BBWordToken(0, 8, 'cc'),
            t.BracketRightToken(0, 10),
            t.TextToken(0, 11, 'text'),
            t.BracketLeftToken(0, 15),
            t.SlashToken(0, 16),
            t.BBWordToken(0, 17, 'aa'),
            t.BracketRightToken(0, 19),
            t.EndToken(0, 20)
        ])

    def test_bbcode_with_string_literals(self):
        input_string = r'["escaped \"\\[] string" /]' 
        tokens = lex(input_string)
        self.assertEqual(tokens, [
            t.BracketLeftToken(0, 0),
            t.StringToken(0, 1, r'escaped "\[] string'),
            t.SpaceToken(0, 24, ' '),
            t.SlashToken(0, 25),
            t.BracketRightToken(0, 26),
            t.EndToken(0, 27)
        ])

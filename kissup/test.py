import unittest

from kissup import lexer


def lex(s):
    return list(lexer.lex_kissup(s))


class TestLexer(unittest.TestCase):
    def test_simple(self):
        self.assertEqual(lex('['), [
            lexer.BracketLeftToken(0, 0),
            lexer.EndToken(0, 1)
        ])
        self.assertEqual(lex('a'), [
            lexer.TextToken(0, 0, 'a'),
            lexer.EndToken(0, 1)
        ])
        self.assertEqual(lex('a['), [
            lexer.TextToken(0, 0, 'a'),
            lexer.BracketLeftToken(0, 1, '['),
            lexer.EndToken(0, 2)
        ])

    def test_text_good_escapes(self):
        input_str = r'abcd\\ fooey \[ \]'
        expected_output_str = r'abcd\ fooey [ ]'
        self.assertEqual(lex(input_str), [
            lexer.TextToken(0, 0, expected_output_str),
            # End token comes at the end of the *input* string!
            lexer.EndToken(0, len(input_str))
        ])

    def test_text_bad_escapes(self):
        with self.assertRaises(lexer.LexError):
            lex(r'\z')
        with self.assertRaises(lexer.LexError):
            lex("\\")

    def test_stuff_that_fails_outside_brackets(self):
        with self.assertRaises(lexer.LexError):
            lex(']')

    def test_bbcode(self):
        tokens = lex("[aa  bb=cc]text[/aa]")
        self.assertEqual(tokens, [
            lexer.BracketLeftToken(0, 0),
            lexer.BBWordToken(0, 1, 'aa'),
            lexer.SpaceToken(0, 3, '  '),
            lexer.BBWordToken(0, 5, 'bb'),
            lexer.EqualsToken(0, 7),
            lexer.BBWordToken(0, 8, 'cc'),
            lexer.BracketRightToken(0, 10),
            lexer.TextToken(0, 11, 'text'),
            lexer.BracketLeftToken(0, 15),
            lexer.SlashToken(0, 16),
            lexer.BBWordToken(0, 17, 'aa'),
            lexer.BracketRightToken(0, 19),
            lexer.EndToken(0, 20)
        ])


if __name__ == '__main__':
    unittest.main()

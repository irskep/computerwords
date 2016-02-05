import unittest

from kissup import lexer


def lex(s):
    return list(lexer.lex_kissup(s))


class TestLexer(unittest.TestCase):
    def test_single_tokens_outside_brackets(self):
        self.assertEqual(lex('['), [
            lexer.BracketLeftToken(0, 0),
            lexer.EndToken(0, 1)
        ])
        self.assertEqual(lex('a'), [
            lexer.TextToken(0, 0, 'a'),
            lexer.EndToken(0, 1)
        ])


    def test_text_escaping(self):
        input_str = r'abcd\\ fooey \[ \]'
        expected_output_str = r'abcd\ fooey [ ]'
        self.assertEqual(lex(input_str), [
            lexer.TextToken(0, 0, expected_output_str),
            # End token comes at the end of the *input* string!
            lexer.EndToken(0, len(input_str))
        ])

    def test_stuff_that_fails_outside_brackets(self):
        with self.assertRaises(lexer.LexError):
            lex(']')


if __name__ == '__main__':
    unittest.main()

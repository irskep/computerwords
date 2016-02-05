import unittest

from kissup import lexer


def lex(s):
    return list(lexer.lex_kissup(s))


class TestLexer(unittest.TestCase):
    def test_singles(self):
        self.assertEqual(lex('['), [lexer.BracketLeftToken(0, 0, '['), lexer.EndToken(line_num=0, pos=1, value='')])


if __name__ == '__main__':
    unittest.main()

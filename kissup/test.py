import unittest
from textwrap import dedent

from kissup import lexer
from kissup import tokens as t
from kissup import ast
from kissup import parser
from kissup import parser_support


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


class TestParser(unittest.TestCase):
    def setUp(self):
        self.maxDiff = None
        super().setUp()

    def test_parse_token(self):
        tokens = lex('text')
        (text_node, i) = parse_funcs['token_TEXT'](tokens, 0)
        self.assertEqual(i, 1)
        self.assertEqual(
            text_node,
            ast.TokenNode('TEXT', t.TextToken(0, 0, 'text')))

    def test_parse_end_token(self):
        tokens = lex('')
        (token_node, i) = parse_funcs['token_ε'](tokens, 0)
        self.assertEqual(i, 1)
        self.assertEqual(
            token_node,
            ast.TokenNode('ε', t.EndToken(0, 0)))

    def test_stmt_1(self):
        tokens = lex('text')
        (stmt_node, i) = parse_funcs['stmt'](tokens, 0)
        self.assertEqual(i, 1)
        expected_token_node = ast.TokenNode(
            'TEXT', t.TextToken(0, 0, 'text'))
        self.assertEqual(
            stmt_node,
            ast.StmtNode(1, expected_token_node))

    def test_arg_value_1(self):
        tokens = lex('[a_bbword]')
        (stmt_node, i) = parse_funcs['arg_value'](tokens, 1)
        self.assertEqual(i, 2)
        self.assertEqual(
            stmt_node.get_string_for_test_comparison(),
            strip("""
                arg_value_1
                  bbword: token_BBWORD: 'a_bbword'
            """))

    def test_arg_value_2(self):
        tokens = lex(r'["a \" string"]')
        (stmt_node, i) = parse_funcs['arg_value'](tokens, 1)
        self.assertEqual(i, 2)
        self.assertEqual(
            stmt_node.get_string_for_test_comparison(),
            strip("""
                arg_value_2
                  string: token_STRING: 'a \" string'
            """))

    def test_tag_arg(self):
        tokens = lex('[x=y]')
        (stmt_node, i) = parse_funcs['tag_arg'](tokens, 1)
        self.assertEqual(i, 4)
        self.assertEqual(
            stmt_node.get_string_for_test_comparison(),
            strip("""
                tag_arg_1
                  bbword: token_BBWORD: 'x'
                  equals: token_=: '='
                  arg_value: arg_value_1
                    bbword: token_BBWORD: 'y'
            """))

    def test_tag_args_a(self):
        tokens = lex('[ x=y]')
        (stmt_node, i) = parse_funcs['tag_args'](tokens, 1)
        self.assertEqual(i, 5)
        self.assertEqual(
            stmt_node.get_string_for_test_comparison(),
            strip("""
                tag_args_1
                  space: token_SPACE: ' '
                  tag_arg: tag_arg_1
                    bbword: token_BBWORD: 'x'
                    equals: token_=: '='
                    arg_value: arg_value_1
                      bbword: token_BBWORD: 'y'
                  tag_args: tag_args_2
            """))

    def test_tag_args_b(self):
        tokens = lex('[ a="b" x=y]')
        (stmt_node, i) = parse_funcs['tag_args'](tokens, 1)
        self.assertEqual(i, 9)
        self.assertEqual(
            stmt_node.get_string_for_test_comparison(),
            strip("""
                tag_args_1
                  space: token_SPACE: ' '
                  tag_arg: tag_arg_1
                    bbword: token_BBWORD: 'a'
                    equals: token_=: '='
                    arg_value: arg_value_2
                      string: token_STRING: 'b'
                  tag_args: tag_args_1
                    space: token_SPACE: ' '
                    tag_arg: tag_arg_1
                      bbword: token_BBWORD: 'x'
                      equals: token_=: '='
                      arg_value: arg_value_1
                        bbword: token_BBWORD: 'y'
                    tag_args: tag_args_2
            """))

    def test_tag_contents_a(self):
        tokens = lex('[abc]')
        (stmt_node, i) = parse_funcs['tag_contents'](tokens, 1)
        self.assertEqual(i, 2)
        self.assertEqual(
            stmt_node.get_string_for_test_comparison(),
            strip("""
                tag_contents_1
                  bbword: token_BBWORD: 'abc'
                  tag_args: tag_args_2
            """))

    def test_tag_contents_b(self):
        tokens = lex('[abc x=y ]')  # include optional whitespace
        (stmt_node, i) = parse_funcs['tag_contents'](tokens, 1)
        self.assertEqual(i, 6)
        self.assertEqual(
            stmt_node.get_string_for_test_comparison(),
            strip("""
                tag_contents_1
                  bbword: token_BBWORD: 'abc'
                  tag_args: tag_args_1
                    space: token_SPACE: ' '
                    tag_arg: tag_arg_1
                      bbword: token_BBWORD: 'x'
                      equals: token_=: '='
                      arg_value: arg_value_1
                        bbword: token_BBWORD: 'y'
                    tag_args: tag_args_2
            """))

    def test_self_closing_tag(self):
        tokens = lex('[abc /]')
        (stmt_node, i) = parse_funcs['self_closing_tag'](tokens, 0)
        self.assertEqual(i, 5)
        self.assertEqual(
            stmt_node.get_string_for_test_comparison(),
            strip("""
                self_closing_tag_1
                  bracket_left: token_[: '['
                  tag_contents: tag_contents_1
                    bbword: token_BBWORD: 'abc'
                    tag_args: tag_args_2
                  slash: token_/: '/'
                  bracket_right: token_]: ']'
            """))

    def test_open_tag(self):
        tokens = lex('[ abc]')  # include optional whitespace
        (stmt_node, i) = parse_funcs['open_tag'](tokens, 0)
        self.assertEqual(i, 4)
        self.assertEqual(
            stmt_node.get_string_for_test_comparison(),
            strip("""
                open_tag_1
                  bracket_left: token_[: '['
                  tag_contents: tag_contents_1
                    bbword: token_BBWORD: 'abc'
                    tag_args: tag_args_2
                  bracket_right: token_]: ']'
            """))

    def test_close_tag(self):
        tokens = lex('[ /abc]')  # include optional whitespace
        (stmt_node, i) = parse_funcs['close_tag'](tokens, 0)
        self.assertEqual(i, 5)
        self.assertEqual(
            stmt_node.get_string_for_test_comparison(),
            strip("""
                close_tag_1
                  bracket_left: token_[: '['
                  slash: token_/: '/'
                  bbword: token_BBWORD: 'abc'
                  bracket_right: token_]: ']'
            """))

    def test_stmt_1_differently(self):
        tokens = lex('abc')  # include optional whitespace
        (stmt_node, i) = parse_funcs['stmt'](tokens, 0)
        self.assertEqual(i, 1)
        self.assertEqual(
            stmt_node.get_string_for_test_comparison(),
            strip("""
                stmt_1
                  text: token_TEXT: 'abc'
            """))

    def test_stmt_2(self):
        tokens = lex('[abc/]')
        (stmt_node, i) = parse_funcs['stmt'](tokens, 0)
        self.assertEqual(i, 4)
        self.assertEqual(
            stmt_node.get_string_for_test_comparison(),
            strip("""
                stmt_2
                  tag: tag_2
                    self_closing_tag: self_closing_tag_1
                      bracket_left: token_[: '['
                      tag_contents: tag_contents_1
                        bbword: token_BBWORD: 'abc'
                        tag_args: tag_args_2
                      slash: token_/: '/'
                      bracket_right: token_]: ']'
            """))

    def test_stmts_b_2_empty_input(self):
        tokens = lex('')
        (stmt_node, i) = parse_funcs['stmts_b'](tokens, 0)
        self.assertEqual(i, 1) # consumes end token
        self.assertEqual(
            stmt_node.get_string_for_test_comparison(),
            strip("""
                stmts_2
            """))

    def test_stmts_a_2_empty_input(self):
        tokens = lex('')
        (stmt_node, i) = parse_funcs['stmts_a'](tokens, 0)
        self.assertEqual(i, 0)  # does NOT consume end token
        self.assertEqual(
            stmt_node.get_string_for_test_comparison(),
            strip("""
                stmts_2
            """))

    def test_stmts_b_1_self_closing_tag(self):
        tokens = lex('[abc /]')
        (stmt_node, i) = parse_funcs['stmts_b'](tokens, 0)
        self.assertEqual(i, 6)
        self.assertEqual(
            stmt_node.get_string_for_test_comparison(),
            strip("""
                stmts_1
                  stmt: stmt_2
                    tag: tag_2
                      self_closing_tag: self_closing_tag_1
                        bracket_left: token_[: '['
                        tag_contents: tag_contents_1
                          bbword: token_BBWORD: 'abc'
                          tag_args: tag_args_2
                        slash: token_/: '/'
                        bracket_right: token_]: ']'
                  stmts: stmts_2
            """))

    def test_stmts_a_1_self_closing_tag(self):
        tokens = lex('[abc /]')
        (stmt_node, i) = parse_funcs['stmts_a'](tokens, 0)
        self.assertEqual(i, 5)
        self.assertEqual(
            stmt_node.get_string_for_test_comparison(),
            strip("""
                stmts_1
                  stmt: stmt_2
                    tag: tag_2
                      self_closing_tag: self_closing_tag_1
                        bracket_left: token_[: '['
                        tag_contents: tag_contents_1
                          bbword: token_BBWORD: 'abc'
                          tag_args: tag_args_2
                        slash: token_/: '/'
                        bracket_right: token_]: ']'
                  stmts: stmts_2
            """))

    def test_stmts_multiple(self):
        tokens = lex('text[abc /]')
        (stmt_node, i) = parse_funcs['stmts_b'](tokens, 0)
        self.assertEqual(i, 7)
        self.assertEqual(
            stmt_node.get_string_for_test_comparison(),
            strip("""
                stmts_1
                  stmt: stmt_1
                    text: token_TEXT: 'text'
                  stmts: stmts_1
                    stmt: stmt_2
                      tag: tag_2
                        self_closing_tag: self_closing_tag_1
                          bracket_left: token_[: '['
                          tag_contents: tag_contents_1
                            bbword: token_BBWORD: 'abc'
                            tag_args: tag_args_2
                          slash: token_/: '/'
                          bracket_right: token_]: ']'
                    stmts: stmts_2
            """))

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

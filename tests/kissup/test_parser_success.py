import unittest
from textwrap import dedent

from computerwords.markdown_parser import tokens as t
from computerwords.markdown_parser import ast
from computerwords.markdown_parser import parser_support, CFMParserConfig
from computerwords.markdown_parser.html_lexer import lex_html
from computerwords.markdown_parser.src_loc import (
    SourceLocation as L,
    SourceRange as R,
)


DOC_ID = ('test.md',)
DOC_PATH = 'test.md'
def get_config(allowed_tags):
    return CFMParserConfig(
        document_id=DOC_ID, document_path=DOC_PATH, allowed_tags=allowed_tags)


parse_funcs = parser_support.PARSE_FUNC_REGISTRY


def lex(config, s):
    return list(lex_html(config, s))


def strip(s):
    return dedent(s)[1:-1]


def parse_production(name, tokens, i, config):
    return parse_funcs[name](tokens, i, config)


class TestParser(unittest.TestCase):
    def setUp(self):
        self.maxDiff = None
        super().setUp()

    def test_parse_token(self):
        config = get_config(set())
        tokens = lex(config, 'text')
        (text_node, i) = parse_production('token_TEXT', tokens, 0, config)
        self.assertEqual(i, 1)
        self.assertEqual(
            text_node,
            ast.TokenNode('TEXT', t.TextToken(L(0, 0, 0).plus(4), 'text')))

    def test_parse_end_token(self):
        config = get_config(set())
        tokens = lex(config, '')
        (token_node, i) = parse_production('token_ε', tokens, 0, config)
        self.assertEqual(i, 1)
        self.assertEqual(
            token_node,
            ast.TokenNode('ε', t.EndToken(L(0, 0, 0).plus(0))))

    def test_stmt_1(self):
        config = get_config(set())
        tokens = lex(config, 'text')
        (stmt_node, i) = parse_production('stmt', tokens, 0, config)
        self.assertEqual(i, 1)
        expected_token_node = ast.TokenNode(
            'TEXT', t.TextToken(L(0, 0, 0).plus(4), 'text'))
        self.assertEqual(
            stmt_node,
            ast.StmtNode(1, expected_token_node))

    def test_arg_value_1(self):
        config = get_config(set())
        tokens = lex(config, '<a_bbword>')
        (stmt_node, i) = parse_production('arg_value', tokens, 1, config)
        self.assertEqual(i, 2)
        self.assertEqual(
            stmt_node.get_string_for_test_comparison(),
            strip("""
                arg_value_1
                  bbword: token_BBWORD: 'a_bbword'
            """))

    def test_arg_value_2(self):
        config = get_config(set())
        tokens = lex(config, r'<"a \" string">')
        (stmt_node, i) = parse_production('arg_value', tokens, 1, config)
        self.assertEqual(i, 2)
        self.assertEqual(
            stmt_node.get_string_for_test_comparison(),
            strip("""
                arg_value_2
                  string: token_STRING: 'a \" string'
            """))

    def test_tag_arg(self):
        config = get_config(set())
        tokens = lex(config, '<x=y>')
        (stmt_node, i) = parse_production('tag_arg', tokens, 1, config)
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
        config = get_config(set())
        tokens = lex(config, '< x=y>')
        (stmt_node, i) = parse_production('tag_args', tokens, 1, config)
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
        config = get_config(set())
        tokens = lex(config, '< a="b" x=y>')
        (stmt_node, i) = parse_production('tag_args', tokens, 1, config)
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
        config = get_config({'abc'})
        tokens = lex(config, '<abc>')
        (stmt_node, i) = parse_production('tag_contents', tokens, 1, config)
        self.assertEqual(i, 2)
        self.assertEqual(
            stmt_node.get_string_for_test_comparison(),
            strip("""
                tag_contents_1
                  bbword: token_BBWORD: 'abc'
                  tag_args: tag_args_2
            """))

    def test_tag_contents_b(self):
        config = get_config({'abc'})
        tokens = lex(config, '<abc x=y >')  # include optional whitespace
        (stmt_node, i) = parse_production('tag_contents', tokens, 1, config)
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
        config = get_config({'abc'})
        tokens = lex(config, '<abc />')
        (stmt_node, i) = parse_production('self_closing_tag', tokens, 0, config)
        self.assertEqual(i, 5)
        self.assertEqual(
            stmt_node.get_string_for_test_comparison(),
            strip("""
                self_closing_tag_1
                  angle_bracket_left: token_<: '<'
                  tag_contents: tag_contents_1
                    bbword: token_BBWORD: 'abc'
                    tag_args: tag_args_2
                  slash: token_/: '/'
                  angle_bracket_right: token_>: '>'
            """))

    def test_open_tag(self):
        config = get_config({'abc'})
        tokens = lex(config, '< abc>')  # include optional whitespace
        (stmt_node, i) = parse_production('open_tag', tokens, 0, config)
        self.assertEqual(i, 4)
        self.assertEqual(
            stmt_node.get_string_for_test_comparison(),
            strip("""
                open_tag_1
                  angle_bracket_left: token_<: '<'
                  tag_contents: tag_contents_1
                    bbword: token_BBWORD: 'abc'
                    tag_args: tag_args_2
                  angle_bracket_right: token_>: '>'
            """))

    def test_close_tag(self):
        config = get_config({'abc'})
        tokens = lex(config, '< /abc>')  # include optional whitespace
        (stmt_node, i) = parse_production('close_tag', tokens, 0, config)
        self.assertEqual(i, 5)
        self.assertEqual(
            stmt_node.get_string_for_test_comparison(),
            strip("""
                close_tag_1
                  angle_bracket_left: token_<: '<'
                  slash: token_/: '/'
                  bbword: token_BBWORD: 'abc'
                  angle_bracket_right: token_>: '>'
            """))

    def test_stmt_1_differently(self):
        config = get_config(set())
        tokens = lex(config, 'abc')
        (stmt_node, i) = parse_production('stmt', tokens, 0, config)
        self.assertEqual(i, 1)
        self.assertEqual(
            stmt_node.get_string_for_test_comparison(),
            strip("""
                stmt_1
                  text: token_TEXT: 'abc'
            """))

    def test_stmt_2(self):
        config = get_config({'abc'})
        tokens = lex(config, '<abc/>')
        (stmt_node, i) = parse_production('stmt', tokens, 0, config)
        self.assertEqual(i, 4)
        self.assertEqual(
            stmt_node.get_string_for_test_comparison(),
            strip("""
                stmt_2
                  tag: tag_2
                    self_closing_tag: self_closing_tag_1
                      angle_bracket_left: token_<: '<'
                      tag_contents: tag_contents_1
                        bbword: token_BBWORD: 'abc'
                        tag_args: tag_args_2
                      slash: token_/: '/'
                      angle_bracket_right: token_>: '>'
            """))

    def test_stmts_b_2_empty_input(self):
        config = get_config(set())
        tokens = lex(config, '')
        (stmt_node, i) = parse_production('stmts_b', tokens, 0, config)
        self.assertEqual(i, 1) # consumes end token
        self.assertEqual(
            stmt_node.get_string_for_test_comparison(),
            strip("""
                stmts_2
            """))

    def test_stmts_a_2_empty_input(self):
        config = get_config({'abc'})
        tokens = lex(config, '')
        (stmt_node, i) = parse_production('stmts_a', tokens, 0, config)
        self.assertEqual(i, 0)  # does NOT consume end token
        self.assertEqual(
            stmt_node.get_string_for_test_comparison(),
            strip("""
                stmts_2
            """))

    def test_stmts_b_1_self_closing_tag(self):
        config = get_config({'abc'})
        tokens = lex(config, '<abc />')
        (stmt_node, i) = parse_production('stmts_b', tokens, 0, config)
        self.assertEqual(i, 6)
        self.assertEqual(
            stmt_node.get_string_for_test_comparison(),
            strip("""
                stmts_1
                  stmt: stmt_2
                    tag: tag_2
                      self_closing_tag: self_closing_tag_1
                        angle_bracket_left: token_<: '<'
                        tag_contents: tag_contents_1
                          bbword: token_BBWORD: 'abc'
                          tag_args: tag_args_2
                        slash: token_/: '/'
                        angle_bracket_right: token_>: '>'
                  stmts: stmts_2
            """))

    def test_stmts_a_1_self_closing_tag(self):
        config = get_config({'abc'})
        tokens = lex(config, '<abc />')
        (stmt_node, i) = parse_production('stmts_a', tokens, 0, config)
        self.assertEqual(i, 5)
        self.assertEqual(
            stmt_node.get_string_for_test_comparison(),
            strip("""
                stmts_1
                  stmt: stmt_2
                    tag: tag_2
                      self_closing_tag: self_closing_tag_1
                        angle_bracket_left: token_<: '<'
                        tag_contents: tag_contents_1
                          bbword: token_BBWORD: 'abc'
                          tag_args: tag_args_2
                        slash: token_/: '/'
                        angle_bracket_right: token_>: '>'
                  stmts: stmts_2
            """))

    def test_stmts_multiple(self):
        config = get_config({'abc'})
        tokens = lex(config, 'text<abc />')
        (stmt_node, i) = parse_production('stmts_b', tokens, 0, config)
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
                          angle_bracket_left: token_<: '<'
                          tag_contents: tag_contents_1
                            bbword: token_BBWORD: 'abc'
                            tag_args: tag_args_2
                          slash: token_/: '/'
                          angle_bracket_right: token_>: '>'
                    stmts: stmts_2
            """))


if __name__ == '__main__':
    unittest.main()

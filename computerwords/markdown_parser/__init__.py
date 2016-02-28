from .html_lexer import lex_html
from .html_parser import parse_html
from .parse_tree_to_cwdom import parse_tree_to_cwdom


def lex_and_parse_html(string, allowed_tags):
    return parse_html(list(lex_html(string)), allowed_tags=allowed_tags)


def string_to_cwdom(string, allowed_tags):
    return parse_tree_to_cwdom(lex_and_parse_html(string, allowed_tags))

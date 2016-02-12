from .lexer import lex_kissup
from .parser import parse_kissup
from .parse_tree_to_cwdom import parse_tree_to_cwdom


def lex_and_parse_kissup(string, allowed_tags):
    return parse_kissup(list(lex_kissup(string)), allowed_tags=allowed_tags)


def string_to_cwdom(string, allowed_tags):
    return parse_tree_to_cwdom(lex_and_parse_kissup(string, allowed_tags))

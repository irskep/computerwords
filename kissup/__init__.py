from .lexer import lex_kissup
from .parser import parse_kissup

def lex_and_parse_kissup(string, allowed_tags):
    return parse_kissup(list(lex_kissup(string)), allowed_tags=allowed_tags)
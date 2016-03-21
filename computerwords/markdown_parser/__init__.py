from collections import namedtuple

from .html_lexer import lex_html
from .html_parser import parse_html
from .parse_tree_to_cwdom import parse_tree_to_cwdom


CFMParserConfigBase = namedtuple('CFMParserConfigBase', ['allowed_tags', 'document_id'])
class CFMParserConfig(CFMParserConfigBase):
    def __new__(cls, allowed_tags, document_id):
        self = super(CFMParserConfig, cls).__new__(
            cls, allowed_tags=allowed_tags, document_id=document_id)
        assert(isinstance(self.allowed_tags, set))
        assert(isinstance(self.document_id, tuple))
        return self


def lex_and_parse_html(string, config):
    return parse_html(list(lex_html(string)), allowed_tags=config.allowed_tags)


def string_to_cwdom(string, config):
    return parse_tree_to_cwdom(lex_and_parse_html(string, config.allowed_tags))

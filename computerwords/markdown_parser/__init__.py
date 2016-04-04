from collections import namedtuple

from .html_lexer import lex_html
from .html_parser import parse_html
from .parse_tree_to_cwdom import parse_tree_to_cwdom
from .src_loc import SourceLocation


CFMParserConfigBase = namedtuple(
    'CFMParserConfigBase',
    ['allowed_tags', 'document_id', 'document_path', 'relative_to_loc'])
class CFMParserConfig(CFMParserConfigBase):
    def __new__(cls, allowed_tags, document_id, document_path, relative_to_loc=None):
        self = super(CFMParserConfig, cls).__new__(
            cls,
            allowed_tags=allowed_tags,
            document_id=document_id,
            document_path=document_path,
            relative_to_loc=relative_to_loc or SourceLocation(0, 0, 0).as_range)
        assert(isinstance(self.allowed_tags, set))
        assert(isinstance(self.document_id, tuple))
        assert(isinstance(self.document_path, str))
        return self

    def copy_relative_to_loc(self, r2l):
        return CFMParserConfig(
            allowed_tags=self.allowed_tags,
            document_id=self.document_id,
            document_path=self.document_path,
            relative_to_loc=r2l)

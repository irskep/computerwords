from .ast import StmtsNode, TagArgsNode
from .html_parser import ParseError
from computerwords.cwdom.nodes import *
from computerwords.cwdom.NodeStore import NodeStore
from .parse_tree_to_cwdom_util import *


def parse_tree_to_cwdom(root):
    return stmts_to_list(root)


def stmts_to_list(stmts):
    assert type(stmts) is StmtsNode
    if stmts.form_num == 1:
        return [stmt_to_tag_or_text(stmts.stmt)] + stmts_to_list(stmts.stmts)
    else:
        return []

def stmt_to_tag_or_text(stmt):
    if stmt.form_num == 1:
        return CWTextNode(stmt.text.value)
    else:
        tag_node = stmt.tag
        if tag_node.form_num == 1:
            tag_contents = tag_node.open_tag.tag_contents
            return CWTagNode(
                tag_contents.bbword.value,
                tag_contents_to_kwargs(tag_contents),
                stmts_to_list(tag_node.stmts))
        else:
            tag_contents = tag_node.self_closing_tag.tag_contents
            return CWTagNode(
                tag_contents.bbword.value,
                tag_contents_to_kwargs(tag_contents))

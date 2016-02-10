from .ast import StmtsNode, TagArgsNode
from .parser import ParseError
from computerwords.cwdom.CWDOMNode import *
from computerwords.cwdom.NodeStore import NodeStore


class DuplicateArgumentsError(ParseError):
    pass


def parse_tree_to_cwdom(root):
    return NodeStore(CWDOMRootNode(stmts_to_list(root)))


def stmts_to_list(stmts):
    assert type(stmts) is StmtsNode
    if stmts.form_num == 1:
        return [stmt_to_tag_or_text(stmts.stmt)] + stmts_to_list(stmts.stmts)
    else:
        return []

def stmt_to_tag_or_text(stmt):
    if stmt.form_num == 1:
        return CWDOMTextNode(stmt.text.value)
    else:
        tag_node = stmt.tag
        if tag_node.form_num == 1:
            tag_contents = tag_node.open_tag.tag_contents
            return CWDOMTagNode(
                tag_contents.bbword.value,
                tag_contents_to_kwargs(tag_contents),
                stmts_to_list(tag_node.stmts))
        else:
            return CWDOMTagNode(tag_node)


def tag_contents_to_kwargs(tag_contents):
    kwargs = {}
    for tag_arg in tag_args_to_list(tag_contents.tag_args):
        key = tag_arg.bbword.value
        if key in kwargs:
            raise DuplicateArgumentsError(
                tag_arg.bbword.token,
                "Duplicate argument {!r}".format(tag_arg.bbword.value))
        kwargs[key] = get_tag_arg_value(tag_arg)
    return kwargs


def tag_args_to_list(tag_args):
    assert type(tag_args) is TagArgsNode
    if tag_args.form_num == 1:
        return [tag_args.tag_arg] + tag_args_to_list(tag_args.tag_args)
    else:
        return []


def get_tag_arg_value(tag_arg):
    if tag_arg.form_num == 1:
        return tag_arg.arg_value.bbword.value
    else:
        return tag_arg.arg_value.token_TEXT.value

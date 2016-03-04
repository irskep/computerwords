from .ast import TagArgsNode
from .html_parser import ParseError
from computerwords.cwdom.nodes import *


class DuplicateArgumentsError(ParseError):
    pass


def tag_args_to_dict(tag_args):
    kwargs = {}
    for tag_arg in tag_args_to_list(tag_args):
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
    try:
        return tag_arg.arg_value.bbword.value
    except AttributeError:
        return tag_arg.arg_value.string.value

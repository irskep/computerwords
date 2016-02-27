"""
stmts_a -> stmt stmts_a
         | ε

stmts_b -> stmt stmts_b
         | END

stmt -> TEXT
      | tag

tag -> open_tag stmts_a close_tag
     | self_closing_tag

open_tag -> < tag_contents space? >

close_tag -> < space? / BBWORD >

self_closing_tag -> < tag_contents / space? >

tag_contents -> space? BBWORD tag_args space?

tag_args -> tag_arg tag_args
          | ε

tag_arg -> SPACE BBWORD = arg_value

arg_value -> BBWORD
           | STRING

space? -> SPACE
        | ε
"""

from collections import namedtuple
from .ast import *
from .parser_support import *

ParserConfig = namedtuple('ParserConfig', ['allowed_tags'])


class TagMismatchError(ParseError):
    def __init__(self, token1, token2):
        self.token2 = token2
        msg_fmt = (
            "Tag mismatch:" +
            " {tag1} (line {line1}, col {col1}) and" +
            " {tag2} (line {line2}, col {col2})." +
            " Did you forget to close your <{tag1}> tag?")
        msg = msg_fmt.format(
            tag1 = token1.value,
            tag2 = token2.value,
            line1 = token1.line,
            line2 = token2.line,
            col1 = token1.pos,
            col2 = token2.pos)
        super().__init__(token1, msg)


class UnknownTagError(ParseError):
    def __init__(self, tag_name_token):
        super().__init__(
            tag_name_token,
            "Unknown tag: {}".format(tag_name_token.value))


### RULES ###

def token_rule(name):
    def parse_token(tokens, i, config):
        if tokens[i].name == name:
            return (TokenNode(name, tokens[i]), i + 1)
        else:
            return (None, i)
    return parse_token

for name in ('TEXT', '<', '>', '/', '=', '[', ']', 'BBWORD', 'STRING', 'ε', 'SPACE'):
    rule('token_' + name, token_rule(name))

def empty_rule(Cls, form):
    def parse_empty(token, i, config):
        return (Cls(form), i)
    return parse_empty

def tags_should_match(tag_node, config):
    open_tag_name_token = tag_node.open_tag.tag_contents.bbword.token
    open_tag_name = open_tag_name_token.value
    close_tag_name_token = tag_node.close_tag.bbword.token
    close_tag_name = close_tag_name_token.value
    if open_tag_name not in config.allowed_tags:
        raise UnknownTagError(open_tag_name_token)
    if open_tag_name != close_tag_name:
        raise TagMismatchError(open_tag_name_token, close_tag_name_token)
    return True

def self_closing_tag_should_be_allowed(tag_node, config):
    tag_name_token = tag_node.tag_contents.bbword.token
    if config.allowed_tags and tag_name_token.value not in config.allowed_tags:
        raise UnknownTagError(tag_name_token)
    return True

# TODO: don't use deep recursion
#stmts_a -> stmt stmts_a
#         | ε
parse_stmts_a = rule('stmts_a',
    sequence_rule(StmtsNode, 1, 'stmt', 'stmts_a'),
    empty_rule(StmtsNode, 2))

#stmts_b -> stmt stmts_b
#         | END
parse_stmts = rule('stmts_b',
    sequence_rule(StmtsNode, 1, 'stmt', 'stmts_b'),
    sequence_rule(StmtsNode, 2, 'token_ε'),
    error_if_not_success=True)

#stmt -> TEXT
#      | tag
rule('stmt',
    sequence_rule(StmtNode, 1, 'token_TEXT'),
    sequence_rule(StmtNode, 2, 'tag'))

#tag -> open_tag stmts close_tag
#     | self_closing_tag
rule('tag',
    validate(
        tags_should_match,
        sequence_rule(TagNode, 1, 'open_tag', 'stmts_a', 'close_tag')),
    sequence_rule(TagNode, 2, 'self_closing_tag'))

#open_tag -> < tag_contents >
rule('open_tag', sequence_rule(
    OpenTagNode, 1, 'token_<', 'tag_contents', 'token_>'))

#close_tag -> < / BBWORD >
rule('close_tag', sequence_rule(
    CloseTagNode, 1, 'token_<', 'space?', 'token_/', 'token_BBWORD', 'token_>'))

#self_closing_tag -> < tag_contents space? / space? >
rule('self_closing_tag',
    validate(self_closing_tag_should_be_allowed,
        sequence_rule(SelfClosingTagNode, 1,
            'token_<', 'tag_contents', 'space?', 'token_/', 'space?', 'token_>')))

#space? -> SPACE
#        | ε
rule('space?', 
    sequence_rule(OptWhitespaceNode, 1, 'token_SPACE'),
    empty_rule(OptWhitespaceNode, 2))

#tag_contents -> BBWORD tag_args
rule('tag_contents',
    sequence_rule(TagContentsNode, 1, 'space?', 'token_BBWORD', 'tag_args'))

# TODO: don't use deep recursion
#tag_args -> SPACE tag_arg tag_args
#          | ε
rule('tag_args',
    sequence_rule(TagArgsNode, 1, 'token_SPACE', 'tag_arg', 'tag_args'),
    empty_rule(TagArgsNode, 2))

#tag_arg -> BBWORD = arg_value
rule('tag_arg',
    sequence_rule(TagArgNode, 1, 'token_BBWORD', 'token_=', 'arg_value'))

#arg_value -> BBWORD
#           | STRING
rule('arg_value', 
    sequence_rule(ArgValueNode, 1, 'token_BBWORD'),
    sequence_rule(ArgValueNode, 2, 'token_STRING'))


def parse_kissup(tokens, allowed_tags=None):
    if allowed_tags is None:
        allowed_tags = set()
    config = ParserConfig(allowed_tags)
    return call_parse_function('stmts_b', tokens, 0, config)[0]


def parse_open_tag(tokens, allowed_tags=None):
    if allowed_tags is None:
        allowed_tags = set()
    config = ParserConfig(allowed_tags)
    result = call_parse_function('open_tag', tokens, 0, config)
    return result[0] if result else None

def parse_close_tag(tokens, allowed_tags=None):
    if allowed_tags is None:
        allowed_tags = set()
    config = ParserConfig(allowed_tags)
    result = call_parse_function('close_tag', tokens, 0, config)
    return result[0] if result else None

def parse_self_closing_tag(tokens, allowed_tags=None):
    if allowed_tags is None:
        allowed_tags = set()
    config = ParserConfig(allowed_tags)
    result = call_parse_function('self_closing_tag', tokens, 0, config)
    return result[0] if result else None

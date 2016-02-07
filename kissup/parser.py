"""

stmts_a -> stmt stmts_a
         | ε

stmts_b -> stmt stmts_b
         | END

stmt -> TEXT
      | tag

tag -> open_tag stmts_a close_tag
     | self_closing_tag

open_tag -> [ tag_contents space? ]

close_tag -> [ space? / BBWORD ]

self_closing_tag -> [ tag_contents / space? ]

tag_contents -> space? BBWORD tag_args space?

tag_args -> tag_arg tag_args
          | ε

tag_arg -> SPACE BBWORD = arg_value

arg_value -> BBWORD
           | STRING

space? -> SPACE
        | ε
"""

from kissup.ast import *
from kissup.parser_support import *

### RULES ###

def create_token_parser(name):
    def parse_token(tokens, i, is_special=False):
        if tokens[i].name == name:
            return (TokenNode(name, tokens[i]), i + 1)
        else:
            return (None, i)
    return parse_token

for name in ('TEXT', '[', ']', '/', '=', 'BBWORD', 'STRING', 'ε', 'SPACE'):
    rule('token_' + name, create_token_parser(name))

def create_empty_rule(Cls, form):
    def parse_empty(token, i):
        return (Cls(form), i)
    return parse_empty

#stmts_a -> stmt stmts_a
#         | ε
parse_stmts_a = rule('stmts_a',
    sequence_rule(StmtsNode, 1, 'stmt', 'stmts_a'),
    create_empty_rule(StmtsNode, 2))

#stmts_b -> stmt stmts_b
#         | END
parse_stmts = rule('stmts_b',
    sequence_rule(StmtsNode, 1, 'stmt', 'stmts_b'),
    sequence_rule(StmtsNode, 2, 'token_ε'))

#stmt -> TEXT
#      | tag
rule('stmt',
    sequence_rule(StmtNode, 1, 'token_TEXT'),
    sequence_rule(StmtNode, 2, 'tag'))

#tag -> open_tag stmts close_tag
#     | self_closing_tag
rule('tag',
    sequence_rule(TagNode, 1, 'open_tag', 'stmts', 'close_tag'),
    sequence_rule(TagNode, 2, 'self_closing_tag'))

#open_tag -> [ tag_contents ]
rule('open_tag', sequence_rule(
    OpenTagNode, 1, 'token_[', 'tag_contents', 'token_]'))

#close_tag -> [ / BBWORD ]
rule('close_tag', sequence_rule(
    CloseTagNode, 1, 'token_[', 'space?', 'token_/', 'token_BBWORD', 'token_]'))

#self_closing_tag -> [ tag_contents space? / space? ]
rule('self_closing_tag',
    sequence_rule(SelfClosingTagNode, 1,
        'token_[', 'tag_contents', 'space?', 'token_/', 'space?', 'token_]'))

#space? -> SPACE
#        | ε
rule('space?', 
    sequence_rule(OptWhitespaceNode, 1, 'token_SPACE'),
    create_empty_rule(OptWhitespaceNode, 2))

#tag_contents -> BBWORD tag_args
rule('tag_contents',
    sequence_rule(TagContentsNode, 1, 'space?', 'token_BBWORD', 'tag_args'))

#tag_args -> SPACE tag_arg tag_args
#          | ε
rule('tag_args',
    sequence_rule(TagArgsNode, 1, 'token_SPACE', 'tag_arg', 'tag_args'),
    create_empty_rule(TagArgsNode, 2))

#tag_arg -> BBWORD = arg_value
rule('tag_arg', sequence_rule(TagArgNode, 1, 'token_BBWORD', 'token_=', 'arg_value'))

#arg_value -> BBWORD
#           | STRING
rule('arg_value', 
    sequence_rule(ArgValueNode, 1, 'token_BBWORD'),
    sequence_rule(ArgValueNode, 2, 'token_STRING'))


def parse_kissup(tokens):
    return call_parse_function('stmts_b', tokens, 0)[0]

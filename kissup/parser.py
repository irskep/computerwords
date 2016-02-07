"""
// BBWORD: a valid tag name; essentially a string literal terminated by whitespace or a reserved character
// TEXT: non-BBCode text (i.e. string literal)
// BB_VAL: A string literal inside a BBCode tag
// e.g. [img src="foo"] matches [BBWORD BBWORD=BB_VAL]

stmts -> stmt stmts
       | ε

stmt -> TEXT
      | tag

tag -> open_tag stmts close_tag
     | self_closing_tag

open_tag -> [ tag_contents ]

close_tag -> [ / BBWORD ]

self_closing_tag -> [ tag_contents opt_whitespace / opt_whitespace ]

opt_whitespace -> SPACE
                | ε

tag_contents -> BBWORD tag_args

tag_args -> tag_arg tag_args
          | ε

tag_arg -> SPACE BBWORD = arg_value

arg_value -> BBWORD
           | STRING
"""

from kissup.ast import *
from kissup.parser_support import *

### RULES ###

def create_token_parser(name):
    def parse_token(tokens, i):
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

#stmts -> stmt stmts
#       | ε
parse_stmts = rule('stmts',
    sequence_rule(StmtsNode, 1, 'stmt', 'stmts'),
    sequence_rule(StmtsNode, 2, 'token_ε')
)

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
    CloseTagNode, 1, 'token_[', 'token_/', 'token_BBWORD', 'token_]'))

#self_closing_tag -> [ tag_contents opt_whitespace / opt_whitespace ]
rule('self_closing_tag',
    sequence_rule(SelfClosingTagNode, 1,
        'token_[', 'tag_contents', 'opt_whitespace', 'token_/', 'opt_whitespace', 'token_]'))

#opt_whitespace -> SPACE
#                | ε
rule('opt_whitespace', 
    sequence_rule(OptWhitespaceNode, 1, 'token_SPACE'),
    create_empty_rule(OptWhitespaceNode, 2))

#tag_contents -> BBWORD tag_args
rule('tag_contents',
    sequence_rule(TagContentsNode, 1, 'token_BBWORD', 'tag_args'))

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
    (node, i) = call_parse_func('stmts', tokens, 0)
    if i < len(tokens) - 1:
        raise ParseError("Could not match {}".format(tokens[i]))
    else:
        return node
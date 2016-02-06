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

self_closing_tag -> [ tag_contents / ]

tag_contents -> BBWORD tag_args
              | BBWORD

tag_args -> tag_arg tag_args
          | ε

tag_arg -> BBWORD = arg_value

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

for name in ('TEXT', '[', ']', '/', '=', 'BBWORD', 'STRING'):
    rule('token_' + name, create_token_parser(name))

def create_empty_rule(Cls, form):
    def parse_empty(token, i):
        return (Cls.create_form(form), i)
    return parse_empty

#stmts -> stmt stmts
#       | ε
def parse_stmts(tokens, i):
    empty_case = (StmtsNode.create_form(2), i)

    if i >= len(tokens): return empty_case

    form_1 = parse_stmts_1(tokens, i)
    if form_1:
        return form_1
    else:
        return empty_case

parse_stmts_1 = sequence_rule(StmtsNode, 1, 'stmt', 'stmts')
rule('stmts', parse_stmts)

#stmt -> TEXT
#      | tag
rule('stmt', multi_rule(
    sequence_rule(StmtNode, 1, 'token_TEXT'),
    sequence_rule(StmtNode, 2, 'tag')))

#tag -> open_tag stmts close_tag
#     | self_closing_tag
rule('tag', multi_rule(
    sequence_rule(TagNode, 1, 'open_tag', 'stmts', 'close_tag'),
    sequence_rule(TagNode, 2, 'self_closing_tag')))

#open_tag -> [ tag_contents ]
rule('open_tag', sequence_rule(
    OpenTagNode, 1, 'token_[', 'tag_contents', 'token_]'))

#close_tag -> [ / BBWORD ]
rule('close_tag', sequence_rule(
    CloseTagNode, 1, 'token_[', 'token_/', 'token_BBWORD', 'token_]'))

#self_closing_tag -> [ tag_contents / ]
rule('self_closing_tag', sequence_rule(
    SelfClosingTagNode, 1, 'token_[', 'tag_contents', 'token_/', 'token_]'))

#tag_contents -> BBWORD tag_args
#              | BBWORD
rule('tag_contents', multi_rule(
    sequence_rule(TagContentsNode, 1, 'token_BBWORD', 'tag_args'),
    sequence_rule(TagContentsNode, 2, 'token_BBWORD')))

#tag_args -> tag_arg tag_args
#          | ε
rule('tag_args', multi_rule(
    sequence_rule(TagArgsNode, 1, 'tag_arg', 'tag_args'),
    create_empty_rule(TagArgsNode, 2)))

#tag_arg -> BBWORD = arg_value
rule('tag_arg', sequence_rule(TagArgNode, 1, 'token_BBWORD', 'token_=', 'arg_value'))

#arg_value -> BBWORD
#           | STRING
rule('arg_value', multi_rule(
    sequence_rule(ArgValueNode, 1, 'token_BBWORD'),
    sequence_rule(ArgValueNode, 2, 'token_STRING')))

"""
// BB_WORD: a valid tag name; essentially a string literal terminated by whitespace or a reserved character
// TEXT: non-BBCode text (i.e. string literal)
// BB_VAL: A string literal inside a BBCode tag
// e.g. [img src="foo"] matches [BB_WORD BB_WORD=BB_VAL]

stmts -> stmt stmts
       | ε

stmt -> TEXT
      | tag

tag -> open_tag stmts close_tag
     | self_closing_tag

open_tag -> [ tag_contents ]

close_tag -> [ / BB_WORD ]

self_closing_tag -> [ tag_contents / ]

tag_contents -> BB_WORD tag_args
              | BB_WORD

tag_args -> tag_arg tag_args
          | ε

tag_arg -> BB_WORD = arg_value

arg_value -> BB_WORD
           | STRING
"""

from collections import namedtuple
from functools import wraps

class ParseError(Exception):
    def __init__(self, token, msg):
        super().__init__("Line {} col {}: {}".format(token.line, token.pos, msg))

class KissUpASTNode: name = "???"

def create_ast_node(class_name, production_name, form_args):
    class Cls(KissUpASTNode):
        name = production_name
        form_classes = []
        def __init__(self, children=[]):
            super().__init__()
            self.children = children

        @staticmethod
        def create_form(n, *args, **kwargs):
            form = self.form_classes[n](*args, **kwargs)
            for field in form._fields:
                field_name = getattr(form, field).name
                if field != field_name:
                    raise ValueError(
                        "AST doesn't match rule: {}.{} -> {}".format(i
                            class_name, field, field_name))
            return form
    Cls.__name__ = 'class_name'
    print(Cls)

    for i, form_args in enumerate(forms):
        form_name = class_name + "Form" + (i + 1)
        form_class = namedtuple(form_name, form_args)
        Cls.form_classes.append(form_class)
        print(' ', form_class)

    return Cls


class TokenNode(KissUpASTNode):
    def __init__(self, name, token):
        super().__init__()
        self.name = name
        self.token = token


StmtsNode = create_ast_node(
    'StmtsNode', 'stmts',
    [['stmt', 'stmts'], []])

StmtNode = create_ast_node(
    'StmtNode', 'stmt',
    [['text'], ['tag']])

TagNode = create_ast_node(
    'TagNode', 'tag',
    [['open_tag', 'stmts', 'close_tag'], ['self_closing_tag']])

OpenTagNode = create_ast_node(
    'OpenTagNode', 'open_tag',
    [['BRACKET_LEFT', 'tag_contents', 'BRACKET_RIGHT']])

CloseTagNode = create_ast_node(
    'CloseTagNode', 'close_tag',
    [['BRACKET_LEFT', 'SLASH', 'BB_WORD', 'BRACKET_RIGHT']])

SelfClosingTagNode = create_ast_node(
    'SelfClosingTagNode', 'self_closing_tag',
    [['BRACKET_LEFT', 'tag_contents', 'SLASH', 'BRACKET_RIGHT']])

TagContentsNode = create_ast_node(
    'TagContentsNode', 'tag_contents',
    [['BB_WORD', 'tag_args'], ['BB_WORD']])

TagArgsNode = create_ast_node(
    'TagArgsNode', 'tag_args',
    [['tag_arg', 'tag_args'], []])

TagArgNode = create_ast_node(
    'TagArgNode', 'tag_arg',
    [['BB_WORD', 'EQUALS', 'arg_value']])

ArgValueNode = create_ast_node(
    'ArgValueNode', 'arg_value',
    [['BB_WORD'], ['STRING']])

def create_multi_form_parse_fn(name, parse_fns):
    def parse(tokens, i):
        for form_fn in [parse_stmt_1, parse_stmt_2]:
            result = form_fn(tokens, i)
            if result: return result
        return (None, i)
    parse.__name__ = 'parse_' + name
    return parse

def parse_sequence(tokens, i, fns):
    nodes = []
    for fn in fns:
        result = fn(tokens, i)
        if result:
            nodes.append(result[0])
            i = result[1]
        else:
            return None
    return nodes, i

def none_to_duple(result, default):
    if result:
        return result
    else:
        return (None, default)

### RULES ###

def parse_token(tokens, i, name):
    if tokens[i].name == name:
        return (TokenNode(name, tokens[i]), i + 1)
    else:
        return (None, i)

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

def parse_stmts_1(tokens, i):
    (stmt, i) = parse_stmt(tokens, i)
    if not stmt: return None

    (stmts, i) = parse_stmts(tokens, i)
    if not stmts: return None

    return (StmtsNode.create_form(1, stmt, stmts), i3)

#stmt -> TEXT
#      | tag
parse_stmt = create_multi_form_parse_fn('stmt', parse_stmt_1, parse_stmt_2)

def parse_stmt_1(tokens, i):
    (text, i) = parse_token(tokens, i, 'TEXT')
    if text:
        return (StmtNode.create_form(1, text), i)
    else:
        return None

def parse_stmt_2(tokens, i):
    (tag, i) = parse_tag(tokens, i)
    if tag:
        return (StmtNode.create_form(2, tag), i)
    else:
        return None

#tag -> open_tag stmts close_tag
#     | self_closing_tag
parse_tag = create_multi_form_parse_fn('tag', parse_tag_1, parse_tag_2)
def parse_tag_1(tokens, i):
    (nodes, i) = none_to_duple(parse_sequence(parse_open_tag, parse_stmts, parse_close_tag))
    if nodes:
        return (TagNode.create_form(1, *nodes))
    else:
        return None

def parse_tag_2(tokens, i):
    (self_closing_tag, i) = none_to_duple(parse_self_closing_tag(tokens, i))
    if self_closing_tag:
        return (TagNode.create_form(2, self_closing_tag), i)
    else:
        return None


#open_tag -> [ tag_contents ]

#close_tag -> [ / BB_WORD ]

#self_closing_tag -> [ tag_contents / ]

#tag_contents -> BB_WORD tag_args
#              | BB_WORD

#tag_args -> tag_arg tag_args
#          | ε

#tag_arg -> BB_WORD = arg_value

#arg_value -> BB_WORD
#           | STRING

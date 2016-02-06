from collections import namedtuple

class KissUpASTNode: name = "???"

def create_ast_node(class_name, production_name, forms):
    class Cls(KissUpASTNode):
        name = production_name
        form_classes = []
        def __init__(self, children=[]):
            super().__init__()
            self.children = children

        @classmethod
        def create_form(cls, n, *args, **kwargs):
            form = cls.form_classes[n - 1](*args, **kwargs)
            for field in form._fields:
                field_name = getattr(form, field).name
                # if field != field_name:
                #     raise ValueError(
                #         "AST doesn't match rule: {}.{} -> {}".format(
                #             i, class_name, field, field_name))
            return form

        def __eq__(self, other):
            return type(self) is type(other) and self.children == other.children

    Cls.__name__ = class_name
    # print(Cls)

    for i, form_args in enumerate(forms):
        form_name = class_name + "Form" + str(i + 1)
        form_class = namedtuple(form_name, form_args)
        Cls.form_classes.append(form_class)
        # print(' ', form_class, form_class._fields)

    return Cls


class TokenNode(KissUpASTNode):
    def __init__(self, name, token):
        super().__init__()
        self.name = name
        self.token = token

    def __repr__(self):
        return 'TokenNode(name={!r})'.format(self.name)

    def __eq__(self, other):
        return type(self) is type(other) and self.name == other.name and self.token == other.token


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

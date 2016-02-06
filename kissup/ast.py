from collections import namedtuple


class InternalParseError(Exception): pass


class KissUpASTNode:
    name = "???"

    def get_string_for_test_comparison(self, inner_indentation=0):
        return self.name


def create_ast_node(class_name, production_name, forms):
    class Cls(KissUpASTNode):
        name = production_name
        form_classes = []
        def __init__(self, form_num, *args, **kwargs):
            super().__init__()

            for arg in args:
                if arg is None:
                    raise InternalParseError("No None args allowed")

            form = self.form_classes[form_num - 1](*args, **kwargs)
            for field in form._fields:
                field_value_name = getattr(form, field).name
                expected_field_value_name = {
                    'bracket_left': '[',
                    'bracket_right': ']',
                    'equals': '=',
                    'slash': '/',
                }.get(field, field.lower())
                if expected_field_value_name != field_value_name.lower():
                    raise InternalParseError(
                        "AST doesn't match rule: {}.{}.{} -> {}".format(
                            i, class_name, expected_field_value_name, field_value_name))

            self.form_num = form_num
            self.attrs = form

        def get_string_for_test_comparison(self, inner_indentation=2):
            elements = [
                "{}_{}".format(
                    super().get_string_for_test_comparison(inner_indentation),
                    self.form_num)
            ]

            for field in self.attrs._fields:
                value = getattr(self.attrs, field)
                elements.append("{}{}: {}".format(
                    ' ' * inner_indentation,
                    field,
                    value.get_string_for_test_comparison(inner_indentation + 2)
                    ))

            return '\n'.join(elements)

        def __getattr__(self, attr):
            try:
                return super().__getattr__(attr)
            except AttributeError:
                return self.attrs.__getattr__(attr)

        def __eq__(self, other):
            return type(self) is type(other) and self.attrs == other.attrs

        def __repr__(self):
            return "{}(attrs={!r})".format(self.__class__.__name__, self.attrs)

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

    def get_string_for_test_comparison(self, inner_indentation=0):
        return "token_{}: {!r}".format(
            super().get_string_for_test_comparison(inner_indentation),
            self.token.value)

    def __eq__(self, other):
        return type(self) is type(other) and self.name == other.name and self.token == other.token

    def __repr__(self):
        return 'TokenNode(name={!r})'.format(self.name)


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
    [['bracket_left', 'tag_contents', 'bracket_right']])


CloseTagNode = create_ast_node(
    'CloseTagNode', 'close_tag',
    [['bracket_left', 'slash', 'bbword', 'bracket_right']])


SelfClosingTagNode = create_ast_node(
    'SelfClosingTagNode', 'self_closing_tag',
    [['bracket_left', 'tag_contents', 'slash', 'bracket_right']])


TagContentsNode = create_ast_node(
    'TagContentsNode', 'tag_contents',
    [['bbword', 'tag_args'], ['bbword']])


TagArgsNode = create_ast_node(
    'TagArgsNode', 'tag_args',
    [['space', 'tag_arg', 'tag_args'], []])


TagArgNode = create_ast_node(
    'TagArgNode', 'tag_arg',
    [['bbword', 'equals', 'arg_value']])


ArgValueNode = create_ast_node(
    'ArgValueNode', 'arg_value',
    [['bbword'], ['string']])

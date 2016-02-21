import logging
import weakref


log = logging.getLogger(__name__)


class IDGenerator:
    def __init__(self):
        self.next_id = 1

    def get_id(self):
        i = self.next_id
        self.next_id += 1
        return i


id_generator = IDGenerator()


class CWDOMNode:
    def __init__(self, name, children=None):
        super().__init__()

        if children is None:
            children = []

        self.name = name
        self.children = children
        self.data = {}

        self.parent_weakref = None
        self.claim_children()

        self.id = name + ':' + str(id_generator.get_id())

    def claim_children(self):
        for child in self.children:
            child.set_parent(self)

    def set_children(self, children):
        self.children = children
        self.claim_children()

    def get_parent(self):
        if self.parent_weakref is None:
            return None
        else:
            return self.parent_weakref()

    def set_parent(self, new_parent):
        if new_parent is None:
            self.parent_weakref = None
        else:
            self.parent_weakref = weakref.ref(new_parent)

    def copy(self):
        return CWDOMNode(self.name)

    def get_string_for_test_comparison(self, inner_indentation=2):
        elements = [
            "{}({})".format(
                self.name, self.get_args_string_for_test_comparison())
        ]

        for child in self.children:
            inner_str = child.get_string_for_test_comparison(
                inner_indentation + 2)
            elements.append(' ' * inner_indentation + inner_str)

        return '\n'.join(elements)

    def get_args_string_for_test_comparison(self):
        return ""

    def __repr__(self):
        return '{}({!r})'.format(self.name, self.children)

    def __eq__(self, other):
        return (type(self) is type(other) and self.id == other.id)

    def __hash__(self):
        return hash(self.id)


class CWDOMRootNode(CWDOMNode):
    def __init__(self, children=None):
        super().__init__('Root', children)

    def copy(self):
        return CWDOMRootNode()


class CWDOMDocumentNode(CWDOMNode):
    def __init__(self, path, children=None):
        super().__init__('Document', children)
        self.path = path

    def get_args_string_for_test_comparison(self):
        return 'path={!r}'.format(self.path)

    def __repr__(self):
        return '{}(path={!r}, children={!r})'.format(
            self.name, self.path, self.children)

    def copy(self):
        return CWDOMDocumentNode(self.path)


class CWDOMStatementsNode(CWDOMNode):
    def __init__(self, children=None):
        super().__init__('Statements', children)

    def copy(self):
        return CWDOMStatementsNode()


class CWDOMTagNode(CWDOMNode):
    def __init__(self, name, kwargs, children=None):
        super().__init__(name, children)
        assert isinstance(kwargs, dict)
        self.kwargs = kwargs

    def copy(self, name=None, kwargs=None):
        return CWDOMTagNode(
            name=name or self.name,
            kwargs=kwargs or self.kwargs)

    def get_args_string_for_test_comparison(self):
        return 'kwargs={!r}'.format(self.kwargs)

    def __repr__(self):
        return '{}(kwargs={!r}, children={!r}'.format(
            self.name, self.kwargs, self.children)

    def __eq__(self, other):
        return super().__eq__(other) and self.kwargs == other.kwargs

    def __hash__(self):
        return hash(self.id)

    def get_arg(self, name):
        return self.kwargs[name]


class CWDOMTextNode(CWDOMNode):
    def __init__(self, text):
        super().__init__('Text', [])
        self.text = text

    def get_string_for_test_comparison(self, inner_indentation=2):
        return repr(self.text)

    def copy(self):
        return CWDOMTextNode(text=text or self.text)

    def get_args_string_for_test_comparison(self):
        return repr(self.text)

    def __repr__(self):
        return "{}(text={!r})".format(self.name, self.text)


class CWDOMAnchorNode(CWDOMNode):
    def __init__(self, ref_id, children=None):
        super().__init__('Anchor', children)
        self.ref_id = ref_id

    def copy(self):
        return CWDOMAnchorNode(ref_id=ref_id or self.ref_id)

    def __repr__(self):
        return "{}(ref_id={!r})".format(self.name, self.ref_id)

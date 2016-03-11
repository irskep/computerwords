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


class CWNode:
    def __init__(self, name, children=None, document_id=None):
        super().__init__()

        self.document_id = document_id

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
        assert(isinstance(children, list))
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

    def deep_set_document_id(self, new_id):
        self.document_id = new_id
        for child in self.children:
            child.deep_set_document_id(new_id)

    def copy(self):
        return CWNode(self.name, document_id=self.document_id)

    def deepcopy(self):
        node_copy = self.copy()
        node_copy.set_children([child.deepcopy() for child in self.children])
        return node_copy

    def deepcopy_children_from(self, node, at_end=False):
        if at_end:
            self.set_children(self.children + [child.deepcopy() for child in node.children])
        else:
            self.set_children([child.deepcopy() for child in node.children] + self.children)
        return self

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

    def shallow_repr(self):
        return '{}()'.format(self.name)

    def __eq__(self, other):
        return (type(self) is type(other) and self.id == other.id)

    def __hash__(self):
        return hash(self.id)


class CWRootNode(CWNode):
    def __init__(self, children=None, document_id=None):
        super().__init__('Root', children, document_id=document_id)

    def copy(self):
        return CWRootNode(document_id=self.document_id)

    def shallow_repr(self):
        return '{}()'.format(self.name)


class CWDocumentNode(CWNode):
    def __init__(self, path, children=None, document_id=None):
        super().__init__('Document', children, document_id=document_id)
        self.path = path

    def get_args_string_for_test_comparison(self):
        return 'path={!r}'.format(self.path)

    def __repr__(self):
        return '{}(path={!r}, children={!r})'.format(
            self.name, self.path, self.children)

    def shallow_repr(self):
        return '{}(path={!r})'.format(self.name, self.path)

    def copy(self):
        return CWDocumentNode(self.path, document_id=document_id)


class CWTagNode(CWNode):
    def __init__(self, name, kwargs, children=None, document_id=None):
        super().__init__(name, children, document_id=document_id)
        assert isinstance(kwargs, dict)
        self.kwargs = kwargs

    def copy(self, name=None, kwargs=None):
        return CWTagNode(
            name=name or self.name,
            kwargs=kwargs or self.kwargs,
            document_id=self.document_id)

    def get_args_string_for_test_comparison(self):
        return 'kwargs={!r}'.format(self.kwargs)

    def __repr__(self):
        return '{}(kwargs={!r}, children={!r})'.format(
            self.name, self.kwargs, self.children)

    def shallow_repr(self):
        return '{}(kwargs={!r})'.format(self.name, self.kwargs)

    def __eq__(self, other):
        return super().__eq__(other) and self.kwargs == other.kwargs

    def __hash__(self):
        return hash(self.id)

    def get_arg(self, name):
        return self.kwargs[name]


class CWTextNode(CWNode):
    def __init__(self, text, document_id=None, escape=True):
        super().__init__('Text', [], document_id=document_id)
        self.escape = escape
        self.text = text

    def get_string_for_test_comparison(self, inner_indentation=2):
        return repr(self.text)

    def copy(self):
        return CWTextNode(self.text)

    def get_args_string_for_test_comparison(self):
        return repr(self.text)

    def __repr__(self):
        return "{}(text={!r})".format(self.name, self.text)


class CWAnchorNode(CWTagNode):
    def __init__(self, ref_id, kwargs=None, children=None, document_id=None):
        super().__init__(
            'Anchor', kwargs or {}, children, document_id=document_id)
        self.ref_id = ref_id

    def get_args_string_for_test_comparison(self):
        return "ref_id={!r}, kwargs={!r}".format(self.ref_id, self.kwargs)

    def copy(self):
        return CWAnchorNode(
            self.ref_id, self.kwargs, document_id=document_id)

    def __repr__(self):
        return "{}(ref_id={!r}, kwargs={!r}, children={!r})".format(
            self.name, self.ref_id, self.kwargs, self.children)

    def shallow_repr(self):
        return "{}(ref_id={!r}, kwargs={!r})".format(
            self.name, self.ref_id, self.kwargs)


class CWLinkNode(CWNode):
    def __init__(self, ref_id, children=None, document_id=None):
        super().__init__('Link', children, document_id=document_id)
        self.ref_id = ref_id

    def get_args_string_for_test_comparison(self):
        return "ref_id={!r}".format(self.ref_id)

    def copy(self):
        return CWLinkNode(self.ref_id, document_id=self.document_id)

    def __repr__(self):
        return "{}(ref_id={!r}, children={!r})".format(
            self.name, self.ref_id, self.children)

    def shallow_repr(self):
        return "{}(ref_id={!r})".format(self.name, self.ref_id)


class CWDocumentLinkNode(CWNode):
    def __init__(self, target_document_id, children=None, document_id=None):
        super().__init__('DocumentLink', children, document_id=document_id)
        self.target_document_id = target_document_id

    def get_args_string_for_test_comparison(self):
        return "target_document_id={!r}".format(self.target_document_id)

    def copy(self):
        return CWDocumentLinkNode(
            self.target_document_id, document_id=self.document_id)

    def __repr__(self):
        return "{}(target_document_id={!r}, children={!r})".format(
            self.name, self.target_document_id, self.children)

    def shallow_repr(self):
        return "{}(target_document_id={!r})".format(
            self.name, self.target_document_id)

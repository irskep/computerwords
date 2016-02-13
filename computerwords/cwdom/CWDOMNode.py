import weakref


class CWDOMNode:
    def __init__(self, name, children=None):
        super().__init__()

        if children is None:
            children = []

        self.name = name
        self.children = children

        self.parent_weakref = None
        self.claim_children()

    def claim_children(self):
        for child in self.children:
            child.set_parent(self)

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

    def copy(self, name=None):
        return CWDOMNode(name=name or self.name)

    def __repr__(self):
        return '{}({!r})'.format(self.name, self.children)

    def __eq__(self, other):
        return (
            type(self) is type(other) and
            self.name == other.name and
            self.children == other.children)

    def __hash__(self, other):
        return hash(repr(self))


# generally you'll just need a type(x) == CWDOMEndOfInputNode check rather than
# having to actually do anything with this object.
class CWDOMEndOfInputNode(CWDOMNode):
    NAME = "END OF ALL INPUT"
    def __init__(self):
        super().__init__(CWDOMEndOfInputNode.NAME)


class CWDOMRootNode(CWDOMNode):
    def __init__(self, children=None):
        super().__init__('Root', children)

    def copy(self, name=None):
        return CWDOMRootNode()


class CWDOMDocumentNode(CWDOMNode):
    def __init__(self, path, children=None):
        super().__init__('Document', children)

    def copy(self, name=None):
        return CWDOMDocumentNode(path)


class CWDOMStatementsNode(CWDOMNode):
    def __init__(self, children=None):
        super().__init__('Statements', children)

    def copy(self, name=None):
        return CWDOMStatementsNode()


class CWDOMTagNode(CWDOMNode):
    def __init__(self, name, kwargs, children=None):
        super().__init__(name, children)
        self.kwargs = kwargs

    def copy(self, name=None, kwargs=None):
        return CWDOMTagNode(
            name=name or self.name,
            kwargs=kwargs or self.kwargs)

    def __repr__(self):
        return '{}(kwargs={!r}, children={!r}'.format(
            self.name, self.kwargs, self.children)

    def __eq__(self, other):
        return super().__eq__(other) and self.kwargs == other.kwargs

    def get_arg(self, name):
        return self.kwargs[name]


class CWDOMTextNode(CWDOMNode):
    def __init__(self, text):
        super().__init__('Text', [])
        self.text = text

    def copy(self, name=None):
        return CWDOMTextNode(text=text or self.text)

    def __repr__(self):
        return "{}(text={!r})".format(self.name, self.text)


class CWDOMAnchorNode(CWDOMNode):
    def __init__(self, ref_id):
        super().__init__('Anchor', [])
        self.ref_id = ref_id

    def copy(self, name=None):
        return CWDOMAnchorNode(ref_id=ref_id or self.ref_id)

    def __repr__(self):
        return "{}(ref_id={!r})".format(self.name, self.ref_id)

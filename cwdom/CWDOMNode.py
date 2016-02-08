class CWDOMNode:
    def __init__(self, name, children=None):
        if children is None:
            children = []

        self.name = name
        self.children = children

        super().__init__()

    def __repr__(self):
        return '{}({!r})'.format(self.name, self.children)

    def __eq__(self, other):
        return (
            type(self) is type(other) and
            self.name == other.name and
            self.children == other.children)

    def __hash__(self, other):
        return hash(repr(self))


class CWDOMRootNode(CWDOMNode):
    def __init__(self, children):
        super().__init__('Root', children)


class CWDOMStatementsNode(CWDOMNode):
    def __init__(self, children):
        super().__init__('Statements', children)


class CWDOMTagNode(CWDOMNode):
    def __init__(self, name, kwargs, children):
        self.kwargs = kwargs
        super().__init__(name, children)

    def __repr__(self):
        return '{}(kwargs={!r}, children={!r}'.format(
            self.name, self.kwargs, self.children)

    def __eq__(self, other):
        return super().__eq__(other) and self.kwargs == other.kwargs

    def get_arg(self, name):
        return self.kwargs[name]


class CWDOMTextNode(CWDOMNode):
    def __init__(self, text):
        self.text = text
        super().__init__('Text', [])

    def __repr__(self):
        return "{}(text={!r})".format(self.name, self.text)
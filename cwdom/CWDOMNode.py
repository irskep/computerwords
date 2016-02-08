class CWDOMNode:
    def __init__(self, tag_name ,children=None):
        if children is None:
            children = []

        self.tag_name = tag_name
        self.children = children

        super().__init__()

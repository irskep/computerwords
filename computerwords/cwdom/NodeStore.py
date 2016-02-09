class NodeStore:
    def __init__(self, root):
        self.root = root
        super().__init__()

    def __repr__(self):
        return 'NodeStore(root={!r})'.format(self.root)

    def __eq__(self, other):
        return type(self) is type(other) and self.root == other.root

    def replace(self, from_node, to_node):
        parent = from_node.get_parent()
        if parent is not None:
            to_node.set_parent(parent)
            from_node.set_parent(None)
            i = parent.children.index(from_node)
            parent.children[i] = to_node
        to_node.children = from_node.children
        to_node.claim_children()

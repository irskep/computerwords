class NodeStore:
    def __init__(self, root):
        super().__init__()
        self.root = root

    def __repr__(self):
        return 'NodeStore(root={!r})'.format(self.root)

    def __eq__(self, other):
        return type(self) is type(other) and self.root == other.root

    # TODO: don't use deep recursion
    def iterate_preorder(self, node=None):
        node = node or self.root
        yield node
        for child in node.children:
            yield child
            yield from self.iterate_preorder(child)

    def visit_all(self, node_name_to_visitor, node=None):
        node = node or self.root
        node_name_to_visitor[node.name].before_children(node)
        for child in node.children:
            self.visit_all(node_name_to_visitor, child)
        node_name_to_visitor[node.name].after_children(node)


    def replace(self, from_node, to_node):
        parent = from_node.get_parent()
        if parent is not None:
            to_node.set_parent(parent)
            from_node.set_parent(None)
            i = parent.children.index(from_node)
            parent.children[i] = to_node
        to_node.children = from_node.children
        to_node.claim_children()


class NodeStoreVisitor:
    def before_children(self, node):
        pass

    def after_children(self, node):
        pass

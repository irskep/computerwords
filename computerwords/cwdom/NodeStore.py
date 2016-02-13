class NodeStore:
    def __init__(self, root):
        super().__init__()
        self.root = root

        # The library is free to add and use data it wants here.
        self.library_data = {}

    def __repr__(self):
        return 'NodeStore(root={!r})'.format(self.root)

    def __eq__(self, other):
        return type(self) is type(other) and self.root == other.root

    def preorder_traversal(self, node=None):
        stack = [node or self.root]
        while len(stack) > 0:
            node = stack.pop()
            yield node
            for child in node.children:
                stack.append(child)

    def process_library(self, library):
        for node in self.preorder_traversal():
            library.process_node(self, node)

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

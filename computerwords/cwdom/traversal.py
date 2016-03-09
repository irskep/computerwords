from collections import deque


def preorder_traversal(node):
    """Yields every node in the tree in pre-order"""
    stack = deque([node])
    while len(stack) > 0:
        node = stack.pop()
        yield node
        for child in reversed(node.children):
            stack.append(child)

def postorder_traversal(node):
    """
    Yields every node in the tree in post-order. Mutation is disallowed.
    """
    root = node
    stack = deque([(root, 'yield'), (root, 'add_children')])
    while len(stack) > 0:
        (node, action) = stack.pop()
        if action == 'yield':
            yield node
        elif action == 'add_children':
            for i in reversed(range(len(node.children))):
                stack.append((node.children[i], 'yield'))
                stack.append((node.children[i], 'add_children'))


class PostorderTraverser:
    """
    A fancy iterator that lets you replace the "cursor", mostly so you
    can mutate the current node while iterating over the tree.

    Also allows mutation of the cursor's ancestors, since they haven't been
    visited yet.
    """
    def __init__(self, node):
        super().__init__()
        self.cursor = node
        self._is_first_result = True

    def replace_cursor(self, new_cursor):
        """Only use this if you really know what you are doing."""
        self.cursor = new_cursor

    def __iter__(self):
        return self

    def __next__(self):
        if self._is_first_result:
            self._descend()
            self._is_first_result = False
        else:
            parent = self.cursor.get_parent()
            if not parent:
                raise StopIteration()

            child_i = parent.children.index(self.cursor)
            next_child_i = child_i + 1
            if next_child_i >= len(parent.children):
                self.cursor = parent
            else:
                self.cursor = parent.children[next_child_i]
                self._descend()
        return self.cursor

    def _descend(self):
        while self.cursor.children:
            self.cursor = self.cursor.children[0]


class MissingVisitorError(Exception): pass


def visit_tree(tree, node_name_to_visitor, node=None):
    """
    Recursively call the CWTreeVisitor for each node. If a node
    is encountered that has no corresponding visitor, an error is thrown.
    """
    node = node or tree.root
    try:
        visitor = node_name_to_visitor[node.name]
    except KeyError:
        raise MissingVisitorError(
            "No visitor registered for {!r}".format(node.name))
    visitor.before_children(tree, node)
    for child in node.children:
        visit_tree(tree, node_name_to_visitor, child)
    visitor.after_children(tree, node)


class CWTreeVisitor:
    def before_children(self, tree, node):
        pass

    def after_children(self, tree, node):
        pass

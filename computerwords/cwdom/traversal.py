"""
Utilities for traversing `CWNode` trees
"""

from collections import deque


def preorder_traversal(node) -> "iterator(CWNode)":
    """
    Yields every node in the tree. Each node is yielded before its descendants.
    Mutation is disallowed.
    """
    stack = deque([node])
    while len(stack) > 0:
        node = stack.pop()
        yield node
        for child in reversed(node.children):
            stack.append(child)

def postorder_traversal(node) -> "iterator(CWNode)":
    """
    Yields every node in the tree. Each node is yielded after its descendants.
    Mutation is disallowed.
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
    A class that lets you iterate over a tree while mutating it.

    Keeps track of a *cursor* representing the last visited node. Each time
    the next node is requested, the iterator looks at the cursor and walks
    up the tree to find the cursor's next sibling or parent.

    You may replace the cursor if you want to replace the node currently being
    visited.

    You may safely mutate the cursor's ancestors, since they haven't been
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

    def __next__(self) -> "CWNode":
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


def iterate_parents(node):
    node = node.get_parent()
    while node:
        yield node
        node = node.get_parent()


def find_ancestor(node, predicate):
    for ancestor in iterate_parents(node):
        if predicate(ancestor):
            return ancestor


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

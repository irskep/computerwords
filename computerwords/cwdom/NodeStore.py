import logging
import re

from collections import deque, namedtuple


log = logging.getLogger(__name__)


NodeAndTraversalKey = namedtuple(
    'NodeAndTraversalKey', ['node', 'traversal_key'])


class MissingVisitorError(Exception): pass
class NodeStoreConsistencyError(Exception): pass


class NodeStore:
    def __init__(self, root):
        super().__init__()
        self.root = root

    ### operators and builtins ###

    def __repr__(self):
        return 'NodeStore(root={!r})'.format(self.root)

    def __eq__(self, other):
        return type(self) is type(other) and self.root == other.root

    ### general utilities ###

    def preorder_traversal(self, node=None):
        """Yields every node in the tree in pre-order"""
        stack = [node or self.root]
        while len(stack) > 0:
            node = stack.pop()
            yield node
            for child in reversed(node.children):
                stack.append(child)

    def postorder_traversal(self, node=None):
        """
        Yields every node in the tree in post-order. Mutation is disallowed.
        """
        root = node or self.root
        stack = deque([(root, 'yield'), (root, 'add_children')])
        while len(stack) > 0:
            (node, action) = stack.pop()
            if action == 'yield':
                yield node
            elif action == 'add_children':
                for i in reversed(range(len(node.children))):
                    stack.append((node.children[i], 'yield'))
                    stack.append((node.children[i], 'add_children'))

    def postorder_traversal_allowing_ancestor_mutations(self, node=None):
        """
        Yields every node in the tree in post-order.

        While running, you may modify, replace, or add ancestors of a node.
        """
        cursor = node or self.root
        while cursor.children:
            cursor = cursor.children[0]
        while True:
            yield cursor
            parent = cursor.get_parent() 
            if not parent: break
            child_i = parent.children.index(cursor)
            next_child_i = child_i + 1
            if next_child_i >= len(parent.children):
                cursor = parent
            else:
                cursor = parent.children[next_child_i]
                while cursor.children:
                    cursor = cursor.children[0]

    ### processing API ###

    def apply_library(self, library, initial_data=None):
        self.processor_data = initial_data or {}
        self._dirty_nodes = set()
        self._removed_nodes = set()
        self._known_ref_ids = set()
        for node in self.postorder_traversal_allowing_ancestor_mutations():
            self._active_node = node
            if self._active_node in self._removed_nodes:
                raise NodeStoreConsistencyError("This can't happen")
            library.run_processors(self, self._active_node)

        # keep doing full passes until no more dirty nodes.
        # future optimization: remember traversal order and sort dirty nodes
        # by that instead of doing another full pass.
        dirty_nodes = self._dirty_nodes
        self._dirty_nodes = set()
        while dirty_nodes:
            for node in self.postorder_traversal_allowing_ancestor_mutations():
                if node not in dirty_nodes:
                    continue

                self._active_node = node
                if self._active_node in self._removed_nodes:
                    continue
                library.run_processors(self, self._active_node)
            dirty_nodes = self._dirty_nodes
            self._dirty_nodes = set()

    def mark_node_dirty(self, node):
        self._dirty_nodes.add(node)

    def get_is_node_dirty(self, node):
        return node in self._dirty_nodes

    def get_was_node_removed(self, node):
        return node in self._removed_nodes

    def _simple_wrap(self, inner_node, outer_node):
        parent = inner_node.get_parent()
        child_i = parent.children.index(inner_node)
        parent.children[child_i] = outer_node
        outer_node.children = [inner_node]
        outer_node.set_parent(parent)
        inner_node.set_parent(outer_node)
        if parent.name == 'Anchor':
            raise ValueError()

    def _wrap_descendant_of_active_node(self, inner_node, outer_node):
        self._simple_wrap(inner_node, outer_node)
        self.mark_node_dirty(outer_node)

    def wrap_node(self, inner_node, outer_node):
        if outer_node.children:
            raise NodeStoreConsistencyError(
                "When wrapping a node, outer node must have no existing"
                " children")
        if self.get_is_descendant(inner_node, self._active_node):
            self._wrap_descendant_of_active_node(inner_node, outer_node)
        else:
            self._simple_wrap(inner_node, outer_node)

    def _mark_subtree_removed(self, node):
        self._removed_nodes.add(node)
        for child in node.children:
            self._mark_subtree_removed(child)

    def _mark_subtree_dirty(self, node):
        self._dirty_nodes.add(node)
        for child in node.children:
            self._dirty_nodes.add(child)

    def replace_subtree(self, old_node, new_node):
        if not self.get_is_descendant(old_node, self._active_node):
            raise NodeStoreConsistencyError(
                "You may only replace subtrees inside the active node.")
        parent = old_node.get_parent()
        child_i = parent.children.index(old_node)
        self._mark_subtree_removed(old_node)
        parent.children[child_i] = new_node
        new_node.set_parent(parent)
        self._mark_subtree_dirty(new_node)

    def insert_subtree(self, parent, i, child):
        if not (
                self.get_is_descendant(parent, self._active_node) or
                parent == self._active_node):
            raise NodeStoreConsistencyError(
                "You may only insert subtrees inside the active node.")
        parent.children.insert(i, child)
        child.set_parent(parent)
        self._mark_subtree_dirty(child)

    def get_is_descendant(self, maybe_descendant, maybe_ancestor):
        parent = maybe_descendant.get_parent()
        while parent:
            if parent == maybe_ancestor:
                return True
            parent = parent.get_parent()
        return False

    def text_to_ref_id(self, text):
        """Returns a ref_id that is unique against all other ref_ids returned
        by this function"""
        ref_id_base = re.sub(r'\W+', '-', text)
        if ref_id_base not in self._known_ref_ids:
            self._known_ref_ids.add(ref_id_base)
            return ref_id_base
        i = 1
        while ref_id_base + '-' + str(i) in self._known_ref_ids:
            i += 1
        ref_id = ref_id_base + '-' + str(i)
        self._known_ref_ids.add(ref_id)
        return ref_id

    ### Methods used primarily by output step ###

    def visit_all(self, node_name_to_visitor, node=None):
        """
        Recursively call the NodeStoreVisitor for each node. If a node
        is encountered that has no corresponding visitor, an error is thrown.
        """
        node = node or self.root
        try:
            visitor = node_name_to_visitor[node.name]
        except KeyError:
            raise MissingVisitorError(
                "No visitor registered for {!r}".format(node.name))
        visitor.before_children(node)
        for child in node.children:
            self.visit_all(node_name_to_visitor, child)
        visitor.after_children(node)


class NodeStoreVisitor:
    def before_children(self, node):
        pass

    def after_children(self, node):
        pass

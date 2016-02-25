import logging
import re

from collections import namedtuple
from .traversal import (
    preorder_traversal,
    postorder_traversal,
    PostorderTraverser,
)


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
        return preorder_traversal(node or self.root)

    def postorder_traversal(self, node=None):
        """
        Yields every node in the tree in post-order. Mutation is disallowed.
        """
        return postorder_traversal(node or self.root)

    def postorder_traversal_allowing_ancestor_mutations(self, node=None):
        """
        Yields every node in the tree in post-order.

        While running, you may modify, replace, or add ancestors of a node.
        """
        return PostorderTraverser(node or self.root)

    def copy_tree(self, node):
        node_copy = node.copy()
        node.set_children([self.copy_tree(child) for child in node.children])

    ### processing API ###

    def _first_pass(self, library):
        self._replacement_node = None
        self._traverser = PostorderTraverser(self.root)
        for node in self._traverser:
            self._process_node_for_first_pass(library, node)

    def _process_node_for_first_pass(self, library, node):
        self._active_node = node
        self._replacement_node = None

        # in case a processor dirtied a node still in the future...
        if node in self._dirty_nodes:
            self._dirty_nodes.remove(node)
        # the algorithm shouldn't let this happen. it's a bug if you see it.
        if self._active_node in self._removed_nodes:
            raise NodeStoreConsistencyError("This can't happen")
        library.run_processors(self, self._active_node)

        # keep re-processing current node as long as it keeps replacing
        # itself
        if self._replacement_node: 
            self._process_node_for_first_pass(library, self._replacement_node)

    def _second_pass(self, library):
        # keep doing full passes until no more dirty nodes.
        # future optimization: remember traversal order and sort dirty nodes
        # by that instead of doing another full pass.
        dirty_nodes = self._dirty_nodes
        self._dirty_nodes = set()
        self._replacement_node = None
        while dirty_nodes:
            self._traverser = PostorderTraverser(self.root)
            for node in self._traverser:
                if node not in dirty_nodes: continue
                if node in self._removed_nodes: continue
                self._process_node_for_second_pass(library, node)
            dirty_nodes = self._dirty_nodes
            self._dirty_nodes = set()

    def _process_node_for_second_pass(self, library, node):
        self._active_node = node
        self._replacement_node = None
        library.run_processors(self, self._active_node)
        while self._replacement_node: 
            self._process_node_for_first_pass(library, self._replacement_node)

    def apply_library(self, library, initial_data=None):
        self.processor_data = initial_data or {}
        self._dirty_nodes = set()
        self._removed_nodes = set()
        self._known_ref_ids = set()

        self._step = 1  # first postorder traversal
        self._first_pass(library)
        self._step = 2  # keep going over any dirty nodes
        self._second_pass(library)

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
        outer_node.document_id = inner_node.document_id
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
        new_node.deep_set_document_id(parent.document_id)
        self._mark_subtree_dirty(new_node)

    def insert_subtree(self, parent, i, child):
        if not (
                self.get_is_descendant(parent, self._active_node) or
                parent == self._active_node):
            raise NodeStoreConsistencyError(
                "You may only insert subtrees inside the active node.")
        parent.children.insert(i, child)
        child.set_parent(parent)
        child.deep_set_document_id(parent.document_id)
        self._mark_subtree_dirty(child)

    def replace_node(self, old_node, new_node):
        if old_node != self._active_node:
            raise NodeStoreConsistencyError(
                "You may only replace the active node.")
        parent = old_node.get_parent()
        child_i = parent.children.index(old_node)
        new_node.set_children(old_node.children)
        parent.children[child_i] = new_node
        new_node.set_parent(parent)
        new_node.document_id = old_node.document_id

        self._removed_nodes.add(old_node)
        self._dirty_nodes.add(new_node)
        self._traverser.replace_cursor(new_node)

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
        visitor.before_children(self, node)
        for child in node.children:
            self.visit_all(node_name_to_visitor, child)
        visitor.after_children(self, node)


class NodeStoreVisitor:
    def before_children(self, node_store, node):
        pass

    def after_children(self, node_store, node):
        pass

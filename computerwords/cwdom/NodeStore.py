import logging
import re

from collections import namedtuple

from computerwords.cwdom.CWDOMNode import CWDOMEndOfInputNode


log = logging.getLogger(__name__)


NodeAndTraversalKey = namedtuple(
    'NodeAndTraversalKey', ['node', 'traversal_key'])


class MissingVisitorError(Exception): pass
class NodeStoreConsistencyError(Exception): pass


# TODO:
# Hash DOM nodes by ID, not full repr
# Enforce mutual exclusion of states:
#   * unvisited
#   * visited + valid
#   * visited + invalid
#   * removed


"""
A node is implicitly invalid iff it has never been visited yet.

A node can be explicitly invalidated at any time.

Visiting a node validates it.
"""


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
        """
        Yields every node in the tree in pre-order. If you mutate the tree
        during the traversal, behavior is undefined.
        """
        stack = [node or self.root]
        while len(stack) > 0:
            node = stack.pop()
            yield node
            for child in reversed(node.children):
                stack.append(child)

    ### processing implementation details ###

    def _preorder_traversal_with_keys(self, node=None):
        """
        Yields every node in the tree in pre-order, paired with a
        "traversal key": a tuple that you can use to sort all results by their
        preorder traversal without actually doing the traversal, or without
        needing to have all nodes present.

        [note]
        A node's children **may** be mutated during traversal! Because
        "preorder" means a parent is visited before its children, the iterator
        doesn't worry about a node's children until it has visited the node.

        This should make it easy to implement simple child-replacement
        processors.
        [/note]

        [warning]
        **However**, you may not mutate a node's **siblings**.
        [/warning]
        """
        node = node or self.root
        stack = [NodeAndTraversalKey(node, ())]
        while len(stack) > 0:
            node_and_traversal_key = stack.pop()
            yield node_and_traversal_key
            (node, traversal_key) = node_and_traversal_key
            new_stack_items = []

            # PROBLEM: we add all children to the stack before any of them are
            # processed. This means that if a processor changes or removes
            # a child, that change will be ignored.
            # SOLUTION: children needs to be a collection that can be iterated
            # over while being mutated.
            i = 0
            while i < len(node.children):
                child = node.children[i]
                new_stack_items.append(
                    NodeAndTraversalKey(child, traversal_key + (i,)))
                i += 1
            for item in reversed(new_stack_items):
                stack.append(item)

    def _process_nodes(self, library, nodes_and_traversal_keys):
        """
        nodes: a list of nodes sorted by their preorder traversal order
        """
        self._nodes_invalidated_this_pass = set()
        self._locked_parent = None
        for node_and_traversal_key in nodes_and_traversal_keys:
            node = node_and_traversal_key.node
            self._locked_parent = node.get_parent()
            self._node_being_processed = node
            self._add_node_to_lists(node)
            self._set_traversal_key(node, node_and_traversal_key.traversal_key)
            # TODO: re-run processors if the node replaces itself?
            # Won't significantly improve runtime upper bound, but might save
            # a lot of allocations.

            # this node might have been added earlier in this pass. if so,
            # we can un-invalidate it, since we won't need to touch it in the
            # next pass.
            if node in self._nodes_invalidated_this_pass:
                self._nodes_invalidated_this_pass.remove(node)
            library.run_processors(self, node)

    def _guard_locked_parent(self, parent, child):
        """
        @param parent: Parent of the node currently being processed[/arg]
        @param child: Node that caller wants to mutate, if relevant
        """
        is_disallowed = (
            parent is self._locked_parent and
            child is not self._node_being_processed)
        if is_disallowed:
            raise NodeStoreConsistencyError((
                "I'm sorry, but you aren't allowed to mutate a node's"
                " siblings in a processor. This is because the traversal"
                " algorithm doesn't yet know how to handle various edge"
                " cases."
            ))

    def _add_node_to_lists(self, node):
        self._node_name_to_nodes.setdefault(node.name, set())
        self._node_name_to_nodes[node.name].add(node)

    def _remove_node(self, node):
        """DOES NOT UNSET PARENT OR REMOVE ITSELF FROM PARENT'S CHILDREN"""
        self._removed_nodes.add(node)
        self._node_name_to_nodes[node.name].remove(node)
        self._set_traversal_key(node, None)
        if node in self._nodes_invalidated_this_pass:
            self._nodes_invalidated_this_pass.remove(node)
        node.children = []

    def _set_traversal_key(self, node, key):
        if key is None:
            if node in self._node_to_traversal_key:
                del self._node_to_traversal_key[node]
            return

        if node in self._node_to_traversal_key:
            existing_key = self._node_to_traversal_key[node]
            if key != existing_key:
                raise NodeStoreConsistencyError(
                    "Node already has a different traversal key")
        else:
            self._node_to_traversal_key[node] = key

    def _replace_traversal_key(self, node, key, ignore_missing=True):
        if node in self._node_to_traversal_key:
            self._node_to_traversal_key[node] = key
        else:
            if ignore_missing:
                pass
            else:
                raise NodeStoreConsistencyError(
                    "Node has no existing traversal key")

    def _recompute_traversal_keys(self, node, key):
        # This could potentially do a LOT of unnecessary work (no-op recursion)
        self._replace_traversal_key(node, key)
        for i, child in enumerate(node.children):
            self._replace_traversal_key(node, key + (i,))

    def _invalidate_node(self, node):
        self._nodes_invalidated_this_pass.add(node)

    ### processing API ###

    def apply_library(self, library, initial_data=None):
        self._removed_nodes = set()
        self._node_name_to_nodes = {}
        self._node_to_traversal_key = {}
        self._known_ref_ids = set()

        if type(self.root.children[-1]) is not CWDOMEndOfInputNode:
            self.root.children.append(CWDOMEndOfInputNode())
        self.processor_data = initial_data or {}

        # look forward to all nodes so that processors can look them up
        # before we've properly reached them
        for node in self.preorder_traversal(self.root):
            self._node_name_to_nodes.setdefault(node.name, set())
            self._node_name_to_nodes[node.name].add(node)

        self._process_nodes(library, self._preorder_traversal_with_keys())

        while self._nodes_invalidated_this_pass:
            self._process_nodes(
                library,
                sorted(
                    NodeAndTraversalKey(node, self.get_traversal_key(node))
                    for node in self._nodes_invalidated_this_pass))

    def get_traversal_key(self, node):
        return self._node_to_traversal_key[node]

    def get_has_node_been_traversed_yet(self, node):
        return node in self._node_to_traversal_key

    def replace_node(self, from_node, to_node):
        """
        Replace node A in the tree with new node B. Node A's children become
        node B's children.
        """
        self._guard_locked_parent(from_node.get_parent(), from_node)
        if self.get_has_node_been_traversed_yet(from_node):
            traversal_key = self.get_traversal_key(from_node)
        else:
            traversal_key = None
        children = from_node.children
        parent = from_node.get_parent()
        parent_children_ix = parent.children.index(from_node)

        if parent is None:
            raise NodeStoreConsistencyError(
                "Can't replace a node that isn't in the tree yet")

        self._remove_node(from_node)

        if traversal_key is not None:
            self._set_traversal_key(to_node, traversal_key)
            self._invalidate_node(to_node)
        to_node.set_children(children)
        parent.children[parent_children_ix] = to_node
        to_node.set_parent(parent)

    def add_node(self, parent, node, i=None):
        """Recursively add node and all its children"""
        self._guard_locked_parent(parent, None)
        if i is None:
            i = len(parent.children)

        if self.get_has_node_been_traversed_yet(parent):
            traversal_key = self.get_traversal_key(parent) + (0,)
            if parent.children:
                if i == 0:
                    # if first, use existing first child's traversal key minus one
                    # in the last component
                    old_key = self.get_traversal_key(parent.children[0])
                    traversal_key = old_key[:-1] + (old_key[-1] - 1,)
                elif i == len(parent.children):
                    old_key = self.get_traversal_key(parent.children[-1])
                    traversal_key = old_key[:-1] + (old_key[-1] + 1,)
                else:
                    # sort just after the previous child
                    traversal_key = (
                        self.get_traversal_key(parent.children[i - 1]) + (0,))
            self._set_traversal_key(node, traversal_key)

        parent.children.insert(i, node)
        node.set_parent(parent)

        self._add_node_to_lists(node)
        self._invalidate_node(node)
        for child in node.children:
            self.add_node(node)

    def remove_node(self, node):
        """Recursively remove node and all its children"""
        self._guard_locked_parent(node.get_parent(), node)
        children = node.children
        self._remove_node(node)
        node.get_parent().children.remove(node)
        for child in children:
            self.remove_node(child)

    def wrap_node(self, inner_node, outer_node):
        """
        inner_node's parent becomes outer-node's parent; inner_node becomes
        outer_node's only child. Only outer_node ends up invalidated.
        """
        self._guard_locked_parent(inner_node.get_parent(), inner_node)
        # replace inner_node's children entry for outer_node with inner_node
        # claim inner_node as child of outer_node
        # recompute traversal keys (blargh)
        parent = inner_node.get_parent()
        i = parent.index(inner_node)
        parent.children[i] = outer_node
        outer_node.set_parent(parent)
        outer_node.set_children(inner_node)

        traversal_key = self.get_traversal_key(inner_node)

        self._recompute_traversal_keys(inner_node, traversal_key + (0,))
        self._add_node_to_lists(outer_node)
        self._set_traversal_key(node, traversal_key)
        self._invalidate_node(outer_node)

    def get_nodes(self, name):
        return frozenset(self._node_name_to_nodes.get(name, set()))

    def get_is_node_invalid(self, node):
        return (
            node in self._nodes_invalidated_this_pass and
            node not in self._removed_nodes)

    def invalidate(self, node):
        self._nodes_invalidated_this_pass.add(node)

    def text_to_ref_id(self, text):
        """Returns a ref_id that is unique against all other ref_ids returned
        by this function"""
        ref_id_base = re.replace(r'\w+', '-', text)
        if ref_id_base not in self._known_ref_ids:
            self._known_ref_ids.add(ref_id_base)
            return ref_id_base
        i = 1
        while ref_id_base + '-' + str(i) in self._known_ref_ids:
            i += 1
        ref_id = ref_id_base + '-' + str(i)
        self._known_ref_ids.add(ref_id)
        return ref_id

    def get_is_node_still_in_tree(self, node):
        return node not in self._removed_nodes

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

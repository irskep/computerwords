import logging
import re

from collections import namedtuple
from .traversal import (
    preorder_traversal,
    postorder_traversal,
    PostorderTraverser,
    iterate_ancestors,
)


log = logging.getLogger(__name__)


class CWTree:
    """
    The `CWTree` class models the tree of all documents and their contents. It
    allows you to traverse the tree in various ways and mutate it during
    some types of traversal.

    Properties:

    * `root`: Root of the tree
    * `env`: Dictionary containing information about how Computer Words
      was invoked and configured. Contains keys `output_dir`, which is a
      `pathlib` path to the root directory of output files, and `config`,
      which is a dict containing the fully resolved configuration.
    * `processor_data`: Dict that you can use to store and retrieve arbitrary
      data during processing.
    """

    def __init__(self, root, env=None):
        super().__init__()
        self.root = root
        self.env = env or {}

    ### operators and builtins ###

    def __repr__(self):
        return 'CWTree(root={!r})'.format(self.root)

    def __eq__(self, other):
        return type(self) is type(other) and self.root == other.root

    ### general utilities ###

    def get_document_path(self, document_id):
        """Returns the path of the source document matching *document_id*"""
        for doc in self.root.children:
            if doc.document_id == document_id:
                return doc.path
        return None

    def preorder_traversal(self, node=None):
        """Shortcut for `computerwords.cwdom.traversal.preorder_traversal()`
        using the root"""
        return preorder_traversal(node or self.root)

    def postorder_traversal(self, node=None):
        """Shortcut for `computerwords.cwdom.traversal.postorder_traversal()`
        using the root"""
        return postorder_traversal(node or self.root)

    def postorder_traversal_allowing_ancestor_mutations(self, node=None):
        """
        Yields every node in the tree in post-order.

        While iterating, you use the mutation methods on this class to mutate
        the tree.
        """
        return PostorderTraverser(node or self.root)

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
            raise CWTreeConsistencyError("This can't happen")
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
        while dirty_nodes:
            self._traverser = PostorderTraverser(self.root)
            for node in self._traverser:
                if node not in dirty_nodes: continue
                if node in self._removed_nodes: continue
                self._process_node_for_second_pass(library, node)
            dirty_nodes = self._dirty_nodes
            self._dirty_nodes = set()

    def _process_node_for_second_pass(self, library, node):
        if node in self._dirty_nodes:
            self._dirty_nodes.remove(node)
        self._active_node = node
        self._replacement_node = None
        library.run_processors(self, self._active_node)
        while self._replacement_node:
            self._process_node_for_second_pass(library, self._replacement_node)

    def _replace_cursor(self, new_node):
        self._traverser.replace_cursor(new_node)
        self._replacement_node = new_node
        self._active_node = new_node

    def apply_library(self, library, initial_data=None):
        """
        Run the processing algorithm on the tree using `library`. Technically
        public, but you probably have no use for this.
        """
        self.processor_data = initial_data or {}
        self._dirty_nodes = set()
        self._removed_nodes = set()
        self._known_ref_ids = set()

        self._step = 1  # first postorder traversal
        self._first_pass(library)
        self._step = 2  # keep going over any dirty nodes
        self._second_pass(library)

    def _mark_node_dirty(self, node):
        self._dirty_nodes.add(node)

    def mark_node_dirty(self, node):
        """
        Ensure this node's processors are run at some point in the future.
        """
        self._mark_node_dirty(node)

    def mark_ancestors_dirty(self, node):
        """
        Ensure this node's ancestors' processors are run at some point in the
        future.
        """
        for parent in iterate_ancestors(node):
            self._mark_node_dirty(parent)

    def _mark_subtree_dirty(self, node):
        self.mark_node_dirty(node)
        for child in node.children:
            self._mark_subtree_dirty(child)

    def get_is_node_dirty(self, node):
        """Returns `True` if the node is marked dirty."""
        return node in self._dirty_nodes

    def get_was_node_removed(self, node):
        """Returns `True` if the node was previously in the tree but has since
        been removed."""
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
        """
        Add an ancestor between `inner_node` and its parent.

        ```graphviz-simple
        A -> C; C -> D; C -> E;
        ```

        ```python
        tree.wrap_node(C, CWNode('B'))
        ```

        ```graphviz-simple
        A -> B; B -> C; C -> D; C -> E;
        ```

        **Limitations**

        * `outer_node` may not have any existing children.
        """
        if outer_node.children:
            raise CWTreeConsistencyError(
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

    def replace_subtree(self, old_node, new_node):
        """
        Replace a node and all its children with another node and all its
        children.

        ```graphviz-simple
        A -> B;
        ```

        ```python
        tree.replace_subtree(B, CWNode('X', [
            CWNode('Y'),
            CWNode('Z'),
        ]))
        ```

        ```graphviz-simple
        A -> X -> Y; X -> Z;
        ```
        """

        if (old_node is self._active_node or
                self.get_is_descendant(old_node, self._active_node)):
            parent = old_node.get_parent()
            child_i = parent.children.index(old_node)
            self._mark_subtree_removed(old_node)

            parent.children[child_i] = new_node
            new_node.set_parent(parent)
            new_node.deep_set_document_id(parent.document_id)
            self._mark_subtree_dirty(new_node)

            if old_node is self._active_node:
                self._replace_cursor(new_node)
        else:
            raise CWTreeConsistencyError(
                "You may only replace subtrees inside the active node.")

    def insert_subtree(self, parent, i, child):
        """
        Adds a note `child` and all its children as a child of `parent` at
        index `i`.

        ```graphviz-simple
        A -> B; A -> C;
        ```

        ```python
        tree.insert_subtree(A, 1, D)
        ```

        ```graphviz-simple
        A -> B; A-> D; A -> C;
        ```

        **Limitations** (may be temporary)

        * `parent` must be the active node or a descendant of it.
        """
        if not (
                self.get_is_descendant(parent, self._active_node) or
                parent == self._active_node):
            raise CWTreeConsistencyError(
                "You may only insert subtrees inside the active node.")
        parent.children.insert(i, child)
        child.set_parent(parent)
        child.deep_set_document_id(parent.document_id)
        self._mark_subtree_dirty(child)

    def add_siblings_ahead(self, new_siblings):
        """
        Add `new_siblings` as children of the active node's parent immediately
        after the active node.

        This may be replaced by a more general method later.

        ```graphviz-simple
        A -> B
        ```

        ```python
        @library.processor('B')
        def process_b(tree, node):
            tree.add_siblings_ahead([CWNode('C'), CWNode('D')])
        ```

        ```graphviz-simple
        A -> B; A -> C; A -> D;
        ```
        """
        node = self._active_node
        parent = node.get_parent()
        child_i = parent.children.index(node)
        for i, sibling in enumerate(new_siblings):
            parent.children.insert(i + 1 + child_i, sibling)
            sibling.set_parent(parent)
            sibling.deep_set_document_id(parent.document_id)
            self._mark_subtree_dirty(sibling)


    def replace_node(self, old_node, new_node):
        """
        Replace `old_node` with `new_node`. Give all of `old_node`'s children
        to `new_node`.

        ```graphviz-simple
        A -> B -> C
        ```

        ```python
        tree.replace_node(B, CWNode('X'))
        ```

        ```graphviz-simple
        A -> X -> C
        ```

        **Limitations** (may be temporary)

        * May only be used on the active node.
        """
        if old_node != self._active_node:
            raise CWTreeConsistencyError(
                "You may only replace the active node.")
        parent = old_node.get_parent()
        child_i = parent.children.index(old_node)
        new_node.set_children(old_node.children)
        parent.children[child_i] = new_node
        new_node.set_parent(parent)
        new_node.document_id = old_node.document_id

        self._removed_nodes.add(old_node)
        self._dirty_nodes.add(new_node)
        self._replace_cursor(new_node)

    def get_is_descendant(self, maybe_descendant, maybe_ancestor):
        """Returns `True` if `maybe_descendant` is a descendant of
        `maybe_ancestor`.
        """
        parent = maybe_descendant.get_parent()
        while parent:
            if parent == maybe_ancestor:
                return True
            parent = parent.get_parent()
        return False

    def text_to_ref_id(self, text):
        """Returns a ref_id that is unique against all other ref_ids returned
        by this function, vaguely resembling `text`"""
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

    def subtree_to_text(self, node):
        """Returns a string of the concatenated text in a subtree"""
        segments = []
        for n in preorder_traversal(node):
            if n.name == 'Text':
                segments.append(n.text)
        return ''.join(segments)


class CWTreeConsistencyError(Exception):
    """Error that is thrown if any of the limitations of `CWTree`'s methods are
    violated"""

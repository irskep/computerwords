<!doctype html>
<html>
    <head>
        <title>computerwords/cwdom/CWTree.py</title>
    </head>
    <body class="autodoc-source">

<a name=0><pre>import logging
</pre></a>
        
<a name=1><pre>import re
</pre></a>
        
<a name=2><pre>
</pre></a>
        
<a name=3><pre>from collections import namedtuple
</pre></a>
        
<a name=4><pre>from .traversal import (
</pre></a>
        
<a name=5><pre>    preorder_traversal,
</pre></a>
        
<a name=6><pre>    postorder_traversal,
</pre></a>
        
<a name=7><pre>    PostorderTraverser,
</pre></a>
        
<a name=8><pre>    iterate_ancestors,
</pre></a>
        
<a name=9><pre>)
</pre></a>
        
<a name=10><pre>
</pre></a>
        
<a name=11><pre>
</pre></a>
        
<a name=12><pre>log = logging.getLogger(__name__)
</pre></a>
        
<a name=13><pre>
</pre></a>
        
<a name=14><pre>
</pre></a>
        
<a name=15><pre>class CWTree:
</pre></a>
        
<a name=16><pre>    """
</pre></a>
        
<a name=17><pre>    The `CWTree` class models the tree of all documents and their contents. It
</pre></a>
        
<a name=18><pre>    allows you to traverse the tree in various ways and mutate it during
</pre></a>
        
<a name=19><pre>    some types of traversal.
</pre></a>
        
<a name=20><pre>    """
</pre></a>
        
<a name=21><pre>
</pre></a>
        
<a name=22><pre>    def __init__(self, root, env=None):
</pre></a>
        
<a name=23><pre>        """
</pre></a>
        
<a name=24><pre>        * `root`: Root of the tree
</pre></a>
        
<a name=25><pre>        * `env`: Dictionary containing information about how Computer Words
</pre></a>
        
<a name=26><pre>          was invoked and configured
</pre></a>
        
<a name=27><pre>        """
</pre></a>
        
<a name=28><pre>        super().__init__()
</pre></a>
        
<a name=29><pre>        self.root = root
</pre></a>
        
<a name=30><pre>        self.env = env or {}
</pre></a>
        
<a name=31><pre>
</pre></a>
        
<a name=32><pre>    ### operators and builtins ###
</pre></a>
        
<a name=33><pre>
</pre></a>
        
<a name=34><pre>    def __repr__(self):
</pre></a>
        
<a name=35><pre>        return 'CWTree(root={!r})'.format(self.root)
</pre></a>
        
<a name=36><pre>
</pre></a>
        
<a name=37><pre>    def __eq__(self, other):
</pre></a>
        
<a name=38><pre>        return type(self) is type(other) and self.root == other.root
</pre></a>
        
<a name=39><pre>
</pre></a>
        
<a name=40><pre>    ### general utilities ###
</pre></a>
        
<a name=41><pre>
</pre></a>
        
<a name=42><pre>    def preorder_traversal(self, node=None):
</pre></a>
        
<a name=43><pre>        """Shortcut for `computerwords.cwdom.traversal.preorder_traversal()`
</pre></a>
        
<a name=44><pre>        using the root"""
</pre></a>
        
<a name=45><pre>        return preorder_traversal(node or self.root)
</pre></a>
        
<a name=46><pre>
</pre></a>
        
<a name=47><pre>    def postorder_traversal(self, node=None):
</pre></a>
        
<a name=48><pre>        """Shortcut for `computerwords.cwdom.traversal.postorder_traversal()`
</pre></a>
        
<a name=49><pre>        using the root"""
</pre></a>
        
<a name=50><pre>        return postorder_traversal(node or self.root)
</pre></a>
        
<a name=51><pre>
</pre></a>
        
<a name=52><pre>    def postorder_traversal_allowing_ancestor_mutations(self, node=None):
</pre></a>
        
<a name=53><pre>        """
</pre></a>
        
<a name=54><pre>        Yields every node in the tree in post-order.
</pre></a>
        
<a name=55><pre>
</pre></a>
        
<a name=56><pre>        While iterating, you use the mutation methods on this class to mutate
</pre></a>
        
<a name=57><pre>        the tree.
</pre></a>
        
<a name=58><pre>        """
</pre></a>
        
<a name=59><pre>        return PostorderTraverser(node or self.root)
</pre></a>
        
<a name=60><pre>
</pre></a>
        
<a name=61><pre>    ### processing API ###
</pre></a>
        
<a name=62><pre>
</pre></a>
        
<a name=63><pre>    def _first_pass(self, library):
</pre></a>
        
<a name=64><pre>        self._replacement_node = None
</pre></a>
        
<a name=65><pre>        self._traverser = PostorderTraverser(self.root)
</pre></a>
        
<a name=66><pre>        for node in self._traverser:
</pre></a>
        
<a name=67><pre>            self._process_node_for_first_pass(library, node)
</pre></a>
        
<a name=68><pre>
</pre></a>
        
<a name=69><pre>    def _process_node_for_first_pass(self, library, node):
</pre></a>
        
<a name=70><pre>        self._active_node = node
</pre></a>
        
<a name=71><pre>        self._replacement_node = None
</pre></a>
        
<a name=72><pre>
</pre></a>
        
<a name=73><pre>        # in case a processor dirtied a node still in the future...
</pre></a>
        
<a name=74><pre>        if node in self._dirty_nodes:
</pre></a>
        
<a name=75><pre>            self._dirty_nodes.remove(node)
</pre></a>
        
<a name=76><pre>        # the algorithm shouldn't let this happen. it's a bug if you see it.
</pre></a>
        
<a name=77><pre>        if self._active_node in self._removed_nodes:
</pre></a>
        
<a name=78><pre>            raise CWTreeConsistencyError("This can't happen")
</pre></a>
        
<a name=79><pre>        library.run_processors(self, self._active_node)
</pre></a>
        
<a name=80><pre>
</pre></a>
        
<a name=81><pre>        # keep re-processing current node as long as it keeps replacing
</pre></a>
        
<a name=82><pre>        # itself
</pre></a>
        
<a name=83><pre>        if self._replacement_node: 
</pre></a>
        
<a name=84><pre>            self._process_node_for_first_pass(library, self._replacement_node)
</pre></a>
        
<a name=85><pre>
</pre></a>
        
<a name=86><pre>    def _second_pass(self, library):
</pre></a>
        
<a name=87><pre>        # keep doing full passes until no more dirty nodes.
</pre></a>
        
<a name=88><pre>        # future optimization: remember traversal order and sort dirty nodes
</pre></a>
        
<a name=89><pre>        # by that instead of doing another full pass.
</pre></a>
        
<a name=90><pre>        dirty_nodes = self._dirty_nodes
</pre></a>
        
<a name=91><pre>        self._dirty_nodes = set()
</pre></a>
        
<a name=92><pre>        while dirty_nodes:
</pre></a>
        
<a name=93><pre>            self._traverser = PostorderTraverser(self.root)
</pre></a>
        
<a name=94><pre>            for node in self._traverser:
</pre></a>
        
<a name=95><pre>                if node not in dirty_nodes: continue
</pre></a>
        
<a name=96><pre>                if node in self._removed_nodes: continue
</pre></a>
        
<a name=97><pre>                if node in self._dirty_nodes:
</pre></a>
        
<a name=98><pre>                    self._dirty_nodes.remove(node)
</pre></a>
        
<a name=99><pre>                self._process_node_for_second_pass(library, node)
</pre></a>
        
<a name=100><pre>            dirty_nodes = self._dirty_nodes
</pre></a>
        
<a name=101><pre>            self._dirty_nodes = set()
</pre></a>
        
<a name=102><pre>
</pre></a>
        
<a name=103><pre>    def _process_node_for_second_pass(self, library, node):
</pre></a>
        
<a name=104><pre>        self._active_node = node
</pre></a>
        
<a name=105><pre>        self._replacement_node = None
</pre></a>
        
<a name=106><pre>        library.run_processors(self, self._active_node)
</pre></a>
        
<a name=107><pre>        while self._replacement_node: 
</pre></a>
        
<a name=108><pre>            self._process_node_for_second_pass(library, self._replacement_node)
</pre></a>
        
<a name=109><pre>
</pre></a>
        
<a name=110><pre>    def _replace_cursor(self, new_node):
</pre></a>
        
<a name=111><pre>        self._traverser.replace_cursor(new_node)
</pre></a>
        
<a name=112><pre>        self._replacement_node = new_node
</pre></a>
        
<a name=113><pre>        self._active_node = new_node
</pre></a>
        
<a name=114><pre>
</pre></a>
        
<a name=115><pre>    def apply_library(self, library, initial_data=None):
</pre></a>
        
<a name=116><pre>        """
</pre></a>
        
<a name=117><pre>        Run the processing algorithm on the tree using `library`. Technically
</pre></a>
        
<a name=118><pre>        public, but you probably have no use for this.
</pre></a>
        
<a name=119><pre>        """
</pre></a>
        
<a name=120><pre>        self.processor_data = initial_data or {}
</pre></a>
        
<a name=121><pre>        self._dirty_nodes = set()
</pre></a>
        
<a name=122><pre>        self._removed_nodes = set()
</pre></a>
        
<a name=123><pre>        self._known_ref_ids = set()
</pre></a>
        
<a name=124><pre>
</pre></a>
        
<a name=125><pre>        self._step = 1  # first postorder traversal
</pre></a>
        
<a name=126><pre>        self._first_pass(library)
</pre></a>
        
<a name=127><pre>        self._step = 2  # keep going over any dirty nodes
</pre></a>
        
<a name=128><pre>        self._second_pass(library)
</pre></a>
        
<a name=129><pre>
</pre></a>
        
<a name=130><pre>    def _mark_node_dirty(self, node):
</pre></a>
        
<a name=131><pre>        self._dirty_nodes.add(node)
</pre></a>
        
<a name=132><pre>
</pre></a>
        
<a name=133><pre>    def mark_node_dirty(self, node):
</pre></a>
        
<a name=134><pre>        """
</pre></a>
        
<a name=135><pre>        Ensure this node's processors are run at some point in the future.
</pre></a>
        
<a name=136><pre>        """
</pre></a>
        
<a name=137><pre>        self._mark_node_dirty(node)
</pre></a>
        
<a name=138><pre>
</pre></a>
        
<a name=139><pre>    def mark_ancestors_dirty(self, node):
</pre></a>
        
<a name=140><pre>        """
</pre></a>
        
<a name=141><pre>        Ensure this node's ancestors' processors are run at some point in the
</pre></a>
        
<a name=142><pre>        future.
</pre></a>
        
<a name=143><pre>        """
</pre></a>
        
<a name=144><pre>        for parent in iterate_ancestors(node):
</pre></a>
        
<a name=145><pre>            self._mark_node_dirty(parent)
</pre></a>
        
<a name=146><pre>
</pre></a>
        
<a name=147><pre>    def _mark_subtree_dirty(self, node):
</pre></a>
        
<a name=148><pre>        self.mark_node_dirty(node)
</pre></a>
        
<a name=149><pre>        for child in node.children:
</pre></a>
        
<a name=150><pre>            self._mark_node_dirty(child)
</pre></a>
        
<a name=151><pre>
</pre></a>
        
<a name=152><pre>    def get_is_node_dirty(self, node):
</pre></a>
        
<a name=153><pre>        """Returns `True` if the node is marked dirty."""
</pre></a>
        
<a name=154><pre>        return node in self._dirty_nodes
</pre></a>
        
<a name=155><pre>
</pre></a>
        
<a name=156><pre>    def get_was_node_removed(self, node):
</pre></a>
        
<a name=157><pre>        """Returns `True` if the node was previously in the tree but has since
</pre></a>
        
<a name=158><pre>        been removed."""
</pre></a>
        
<a name=159><pre>        return node in self._removed_nodes
</pre></a>
        
<a name=160><pre>
</pre></a>
        
<a name=161><pre>    def _simple_wrap(self, inner_node, outer_node):
</pre></a>
        
<a name=162><pre>        parent = inner_node.get_parent()
</pre></a>
        
<a name=163><pre>        child_i = parent.children.index(inner_node)
</pre></a>
        
<a name=164><pre>        parent.children[child_i] = outer_node
</pre></a>
        
<a name=165><pre>        outer_node.children = [inner_node]
</pre></a>
        
<a name=166><pre>        outer_node.set_parent(parent)
</pre></a>
        
<a name=167><pre>        inner_node.set_parent(outer_node)
</pre></a>
        
<a name=168><pre>        outer_node.document_id = inner_node.document_id
</pre></a>
        
<a name=169><pre>        if parent.name == 'Anchor':
</pre></a>
        
<a name=170><pre>            raise ValueError()
</pre></a>
        
<a name=171><pre>
</pre></a>
        
<a name=172><pre>    def _wrap_descendant_of_active_node(self, inner_node, outer_node):
</pre></a>
        
<a name=173><pre>        self._simple_wrap(inner_node, outer_node)
</pre></a>
        
<a name=174><pre>        self.mark_node_dirty(outer_node)
</pre></a>
        
<a name=175><pre>
</pre></a>
        
<a name=176><pre>    def wrap_node(self, inner_node, outer_node):
</pre></a>
        
<a name=177><pre>        """
</pre></a>
        
<a name=178><pre>        Add an ancestor between `inner_node` and its parent.
</pre></a>
        
<a name=179><pre>
</pre></a>
        
<a name=180><pre>        ```graphviz-simple
</pre></a>
        
<a name=181><pre>        A -> C; C -> D; C -> E;
</pre></a>
        
<a name=182><pre>        ```
</pre></a>
        
<a name=183><pre>
</pre></a>
        
<a name=184><pre>        ```python
</pre></a>
        
<a name=185><pre>        tree.wrap_node(C, CWNode('B'))
</pre></a>
        
<a name=186><pre>        ```
</pre></a>
        
<a name=187><pre>
</pre></a>
        
<a name=188><pre>        ```graphviz-simple
</pre></a>
        
<a name=189><pre>        A -> B; B -> C; C -> D; C -> E;
</pre></a>
        
<a name=190><pre>        ```
</pre></a>
        
<a name=191><pre>
</pre></a>
        
<a name=192><pre>        **Limitations**
</pre></a>
        
<a name=193><pre>
</pre></a>
        
<a name=194><pre>        * `outer_node` may not have any existing children.
</pre></a>
        
<a name=195><pre>        """
</pre></a>
        
<a name=196><pre>        if outer_node.children:
</pre></a>
        
<a name=197><pre>            raise CWTreeConsistencyError(
</pre></a>
        
<a name=198><pre>                "When wrapping a node, outer node must have no existing"
</pre></a>
        
<a name=199><pre>                " children")
</pre></a>
        
<a name=200><pre>        if self.get_is_descendant(inner_node, self._active_node):
</pre></a>
        
<a name=201><pre>            self._wrap_descendant_of_active_node(inner_node, outer_node)
</pre></a>
        
<a name=202><pre>        else:
</pre></a>
        
<a name=203><pre>            self._simple_wrap(inner_node, outer_node)
</pre></a>
        
<a name=204><pre>
</pre></a>
        
<a name=205><pre>    def _mark_subtree_removed(self, node):
</pre></a>
        
<a name=206><pre>        self._removed_nodes.add(node)
</pre></a>
        
<a name=207><pre>        for child in node.children:
</pre></a>
        
<a name=208><pre>            self._mark_subtree_removed(child)
</pre></a>
        
<a name=209><pre>
</pre></a>
        
<a name=210><pre>    def replace_subtree(self, old_node, new_node):
</pre></a>
        
<a name=211><pre>        """
</pre></a>
        
<a name=212><pre>        Replace a node and all its children with another node and all its
</pre></a>
        
<a name=213><pre>        children.
</pre></a>
        
<a name=214><pre>
</pre></a>
        
<a name=215><pre>        ```graphviz-simple
</pre></a>
        
<a name=216><pre>        A -> B;
</pre></a>
        
<a name=217><pre>        ```
</pre></a>
        
<a name=218><pre>
</pre></a>
        
<a name=219><pre>        ```python
</pre></a>
        
<a name=220><pre>        tree.replace_subtree(B, CWNode('X', [
</pre></a>
        
<a name=221><pre>            CWNode('Y'),
</pre></a>
        
<a name=222><pre>            CWNode('Z'),
</pre></a>
        
<a name=223><pre>        ]))
</pre></a>
        
<a name=224><pre>        ```
</pre></a>
        
<a name=225><pre>
</pre></a>
        
<a name=226><pre>        ```graphviz-simple
</pre></a>
        
<a name=227><pre>        A -> X -> Y; X -> Z;
</pre></a>
        
<a name=228><pre>        ```
</pre></a>
        
<a name=229><pre>        """
</pre></a>
        
<a name=230><pre>
</pre></a>
        
<a name=231><pre>        if (old_node is self._active_node or
</pre></a>
        
<a name=232><pre>                self.get_is_descendant(old_node, self._active_node)):
</pre></a>
        
<a name=233><pre>            parent = old_node.get_parent()
</pre></a>
        
<a name=234><pre>            child_i = parent.children.index(old_node)
</pre></a>
        
<a name=235><pre>            self._mark_subtree_removed(old_node)
</pre></a>
        
<a name=236><pre>
</pre></a>
        
<a name=237><pre>            parent.children[child_i] = new_node
</pre></a>
        
<a name=238><pre>            new_node.set_parent(parent)
</pre></a>
        
<a name=239><pre>            new_node.deep_set_document_id(parent.document_id)
</pre></a>
        
<a name=240><pre>            self._mark_subtree_dirty(new_node)
</pre></a>
        
<a name=241><pre>
</pre></a>
        
<a name=242><pre>            if old_node is self._active_node:
</pre></a>
        
<a name=243><pre>                self._replace_cursor(new_node)
</pre></a>
        
<a name=244><pre>        else:
</pre></a>
        
<a name=245><pre>            raise CWTreeConsistencyError(
</pre></a>
        
<a name=246><pre>                "You may only replace subtrees inside the active node.")
</pre></a>
        
<a name=247><pre>
</pre></a>
        
<a name=248><pre>    def insert_subtree(self, parent, i, child):
</pre></a>
        
<a name=249><pre>        """
</pre></a>
        
<a name=250><pre>        Adds a note `child` and all its children as a child of `parent` at
</pre></a>
        
<a name=251><pre>        index `i`.
</pre></a>
        
<a name=252><pre>
</pre></a>
        
<a name=253><pre>        ```graphviz-simple
</pre></a>
        
<a name=254><pre>        A -> B; A -> C;
</pre></a>
        
<a name=255><pre>        ```
</pre></a>
        
<a name=256><pre>
</pre></a>
        
<a name=257><pre>        ```python
</pre></a>
        
<a name=258><pre>        tree.insert_subtree(A, 1, D)
</pre></a>
        
<a name=259><pre>        ```
</pre></a>
        
<a name=260><pre>
</pre></a>
        
<a name=261><pre>        ```graphviz-simple
</pre></a>
        
<a name=262><pre>        A -> B; A-> D; A -> C;
</pre></a>
        
<a name=263><pre>        ```
</pre></a>
        
<a name=264><pre>
</pre></a>
        
<a name=265><pre>        **Limitations** (may be temporary)
</pre></a>
        
<a name=266><pre>
</pre></a>
        
<a name=267><pre>        * `parent` must be the active node or a descendant of it.
</pre></a>
        
<a name=268><pre>        """
</pre></a>
        
<a name=269><pre>        if not (
</pre></a>
        
<a name=270><pre>                self.get_is_descendant(parent, self._active_node) or
</pre></a>
        
<a name=271><pre>                parent == self._active_node):
</pre></a>
        
<a name=272><pre>            raise CWTreeConsistencyError(
</pre></a>
        
<a name=273><pre>                "You may only insert subtrees inside the active node.")
</pre></a>
        
<a name=274><pre>        parent.children.insert(i, child)
</pre></a>
        
<a name=275><pre>        child.set_parent(parent)
</pre></a>
        
<a name=276><pre>        child.deep_set_document_id(parent.document_id)
</pre></a>
        
<a name=277><pre>        self._mark_subtree_dirty(child)
</pre></a>
        
<a name=278><pre>
</pre></a>
        
<a name=279><pre>    def add_siblings_ahead(self, new_siblings):
</pre></a>
        
<a name=280><pre>        """
</pre></a>
        
<a name=281><pre>        Add `new_siblings` as children of the active node's parent immediately
</pre></a>
        
<a name=282><pre>        after the active node.
</pre></a>
        
<a name=283><pre>
</pre></a>
        
<a name=284><pre>        This may be replaced by a more general method later.
</pre></a>
        
<a name=285><pre>
</pre></a>
        
<a name=286><pre>        ```graphviz-simple
</pre></a>
        
<a name=287><pre>        A -> B
</pre></a>
        
<a name=288><pre>        ```
</pre></a>
        
<a name=289><pre>
</pre></a>
        
<a name=290><pre>        ```python
</pre></a>
        
<a name=291><pre>        @library.processor('B')
</pre></a>
        
<a name=292><pre>        def process_b(tree, node):
</pre></a>
        
<a name=293><pre>            tree.add_siblings_ahead([CWNode('C'), CWNode('D')])
</pre></a>
        
<a name=294><pre>        ```
</pre></a>
        
<a name=295><pre>
</pre></a>
        
<a name=296><pre>        ```graphviz-simple
</pre></a>
        
<a name=297><pre>        A -> B; A -> C; A -> D;
</pre></a>
        
<a name=298><pre>        ```
</pre></a>
        
<a name=299><pre>        """
</pre></a>
        
<a name=300><pre>        node = self._active_node
</pre></a>
        
<a name=301><pre>        parent = node.get_parent()
</pre></a>
        
<a name=302><pre>        child_i = parent.children.index(node)
</pre></a>
        
<a name=303><pre>        for i, sibling in enumerate(new_siblings):
</pre></a>
        
<a name=304><pre>            parent.children.insert(i + 1 + child_i, sibling)
</pre></a>
        
<a name=305><pre>            sibling.set_parent(parent)
</pre></a>
        
<a name=306><pre>            sibling.deep_set_document_id(parent.document_id)
</pre></a>
        
<a name=307><pre>            self._mark_subtree_dirty(sibling)
</pre></a>
        
<a name=308><pre>            
</pre></a>
        
<a name=309><pre>
</pre></a>
        
<a name=310><pre>    def replace_node(self, old_node, new_node):
</pre></a>
        
<a name=311><pre>        """
</pre></a>
        
<a name=312><pre>        Replace `old_node` with `new_node`. Give all of `old_node`'s children
</pre></a>
        
<a name=313><pre>        to `new_node`.
</pre></a>
        
<a name=314><pre>
</pre></a>
        
<a name=315><pre>        ```graphviz-simple
</pre></a>
        
<a name=316><pre>        A -> B -> C
</pre></a>
        
<a name=317><pre>        ```
</pre></a>
        
<a name=318><pre>
</pre></a>
        
<a name=319><pre>        ```python
</pre></a>
        
<a name=320><pre>        tree.replace_node(B, CWNode('X'))
</pre></a>
        
<a name=321><pre>        ```
</pre></a>
        
<a name=322><pre>
</pre></a>
        
<a name=323><pre>        ```graphviz-simple
</pre></a>
        
<a name=324><pre>        A -> X -> C
</pre></a>
        
<a name=325><pre>        ```
</pre></a>
        
<a name=326><pre>
</pre></a>
        
<a name=327><pre>        **Limitations** (may be temporary)
</pre></a>
        
<a name=328><pre>
</pre></a>
        
<a name=329><pre>        * May only be used on the active node.
</pre></a>
        
<a name=330><pre>        """
</pre></a>
        
<a name=331><pre>        if old_node != self._active_node:
</pre></a>
        
<a name=332><pre>            raise CWTreeConsistencyError(
</pre></a>
        
<a name=333><pre>                "You may only replace the active node.")
</pre></a>
        
<a name=334><pre>        parent = old_node.get_parent()
</pre></a>
        
<a name=335><pre>        child_i = parent.children.index(old_node)
</pre></a>
        
<a name=336><pre>        new_node.set_children(old_node.children)
</pre></a>
        
<a name=337><pre>        parent.children[child_i] = new_node
</pre></a>
        
<a name=338><pre>        new_node.set_parent(parent)
</pre></a>
        
<a name=339><pre>        new_node.document_id = old_node.document_id
</pre></a>
        
<a name=340><pre>
</pre></a>
        
<a name=341><pre>        self._removed_nodes.add(old_node)
</pre></a>
        
<a name=342><pre>        self._dirty_nodes.add(new_node)
</pre></a>
        
<a name=343><pre>        self._replace_cursor(new_node)
</pre></a>
        
<a name=344><pre>
</pre></a>
        
<a name=345><pre>    def get_is_descendant(self, maybe_descendant, maybe_ancestor):
</pre></a>
        
<a name=346><pre>        """Returns `True` if `maybe_descendant` is a descendant of
</pre></a>
        
<a name=347><pre>        `maybe_ancestor`.
</pre></a>
        
<a name=348><pre>        """
</pre></a>
        
<a name=349><pre>        parent = maybe_descendant.get_parent()
</pre></a>
        
<a name=350><pre>        while parent:
</pre></a>
        
<a name=351><pre>            if parent == maybe_ancestor:
</pre></a>
        
<a name=352><pre>                return True
</pre></a>
        
<a name=353><pre>            parent = parent.get_parent()
</pre></a>
        
<a name=354><pre>        return False
</pre></a>
        
<a name=355><pre>
</pre></a>
        
<a name=356><pre>    def text_to_ref_id(self, text):
</pre></a>
        
<a name=357><pre>        """Returns a ref_id that is unique against all other ref_ids returned
</pre></a>
        
<a name=358><pre>        by this function, vaguely resembling `text`"""
</pre></a>
        
<a name=359><pre>        ref_id_base = re.sub(r'\W+', '-', text)
</pre></a>
        
<a name=360><pre>        if ref_id_base not in self._known_ref_ids:
</pre></a>
        
<a name=361><pre>            self._known_ref_ids.add(ref_id_base)
</pre></a>
        
<a name=362><pre>            return ref_id_base
</pre></a>
        
<a name=363><pre>        i = 1
</pre></a>
        
<a name=364><pre>        while ref_id_base + '-' + str(i) in self._known_ref_ids:
</pre></a>
        
<a name=365><pre>            i += 1
</pre></a>
        
<a name=366><pre>        ref_id = ref_id_base + '-' + str(i)
</pre></a>
        
<a name=367><pre>        self._known_ref_ids.add(ref_id)
</pre></a>
        
<a name=368><pre>        return ref_id
</pre></a>
        
<a name=369><pre>
</pre></a>
        
<a name=370><pre>    def subtree_to_text(self, node):
</pre></a>
        
<a name=371><pre>        """Returns a string of the concatenated text in a subtree"""
</pre></a>
        
<a name=372><pre>        segments = []
</pre></a>
        
<a name=373><pre>        for n in preorder_traversal(node):
</pre></a>
        
<a name=374><pre>            if n.name == 'Text':
</pre></a>
        
<a name=375><pre>                segments.append(n.text)
</pre></a>
        
<a name=376><pre>        return ''.join(segments)
</pre></a>
        
<a name=377><pre>
</pre></a>
        
<a name=378><pre>
</pre></a>
        
<a name=379><pre>class CWTreeConsistencyError(Exception):
</pre></a>
        
<a name=380><pre>    """Error that is thrown if any of the limitations of `CWTree`'s methods are
</pre></a>
        
<a name=381><pre>    violated"""
</pre></a>
        
    </body>
</html>
<!doctype html>
<html>
    <head>
        <title>computerwords/cwdom/traversal.py</title>
    </head>
    <body class="autodoc-source">

<a name=0><pre>"""
</pre></a>
        
<a name=1><pre>Utilities for traversing `CWNode` trees.
</pre></a>
        
<a name=2><pre>"""
</pre></a>
        
<a name=3><pre>
</pre></a>
        
<a name=4><pre>from collections import deque
</pre></a>
        
<a name=5><pre>
</pre></a>
        
<a name=6><pre>
</pre></a>
        
<a name=7><pre>def preorder_traversal(node) -> "iterator(CWNode)":
</pre></a>
        
<a name=8><pre>    """
</pre></a>
        
<a name=9><pre>    Yields every node in the tree. Each node is yielded before its descendants.
</pre></a>
        
<a name=10><pre>    Mutation is disallowed.
</pre></a>
        
<a name=11><pre>    """
</pre></a>
        
<a name=12><pre>    stack = deque([node])
</pre></a>
        
<a name=13><pre>    while len(stack) > 0:
</pre></a>
        
<a name=14><pre>        node = stack.pop()
</pre></a>
        
<a name=15><pre>        yield node
</pre></a>
        
<a name=16><pre>        for child in reversed(node.children):
</pre></a>
        
<a name=17><pre>            stack.append(child)
</pre></a>
        
<a name=18><pre>
</pre></a>
        
<a name=19><pre>def postorder_traversal(node) -> "iterator(CWNode)":
</pre></a>
        
<a name=20><pre>    """
</pre></a>
        
<a name=21><pre>    Yields every node in the tree. Each node is yielded after its descendants.
</pre></a>
        
<a name=22><pre>    Mutation is disallowed.
</pre></a>
        
<a name=23><pre>    """
</pre></a>
        
<a name=24><pre>    root = node
</pre></a>
        
<a name=25><pre>    stack = deque([(root, 'yield'), (root, 'add_children')])
</pre></a>
        
<a name=26><pre>    while len(stack) > 0:
</pre></a>
        
<a name=27><pre>        (node, action) = stack.pop()
</pre></a>
        
<a name=28><pre>        if action == 'yield':
</pre></a>
        
<a name=29><pre>            yield node
</pre></a>
        
<a name=30><pre>        elif action == 'add_children':
</pre></a>
        
<a name=31><pre>            for i in reversed(range(len(node.children))):
</pre></a>
        
<a name=32><pre>                stack.append((node.children[i], 'yield'))
</pre></a>
        
<a name=33><pre>                stack.append((node.children[i], 'add_children'))
</pre></a>
        
<a name=34><pre>
</pre></a>
        
<a name=35><pre>
</pre></a>
        
<a name=36><pre>def iterate_ancestors(node):
</pre></a>
        
<a name=37><pre>    """
</pre></a>
        
<a name=38><pre>    Yields every ancestor of a node, starting with its immediate parent.
</pre></a>
        
<a name=39><pre>
</pre></a>
        
<a name=40><pre>    ```python
</pre></a>
        
<a name=41><pre>    from computerwords.cwdom.nodes import CWNode
</pre></a>
        
<a name=42><pre>    from computerwords.cwdom.traversal import iterate_ancestors
</pre></a>
        
<a name=43><pre>    node_c = CWNode('c', [])
</pre></a>
        
<a name=44><pre>    tree = CWNode('a', [
</pre></a>
        
<a name=45><pre>        CWNode('b', [node_c]),
</pre></a>
        
<a name=46><pre>        CWNode('d', []),
</pre></a>
        
<a name=47><pre>    ])
</pre></a>
        
<a name=48><pre>    assert ([node.name for node in iterate_ancestors(node_c)] ==
</pre></a>
        
<a name=49><pre>            ['b', 'a'])
</pre></a>
        
<a name=50><pre>    ```
</pre></a>
        
<a name=51><pre>    """
</pre></a>
        
<a name=52><pre>    node = node.get_parent()
</pre></a>
        
<a name=53><pre>    while node:
</pre></a>
        
<a name=54><pre>        yield node
</pre></a>
        
<a name=55><pre>        node = node.get_parent()
</pre></a>
        
<a name=56><pre>
</pre></a>
        
<a name=57><pre>
</pre></a>
        
<a name=58><pre>def find_ancestor(node, predicate):
</pre></a>
        
<a name=59><pre>    """
</pre></a>
        
<a name=60><pre>    Returns the closest ancestor of a node matching the given predicate.
</pre></a>
        
<a name=61><pre>
</pre></a>
        
<a name=62><pre>    ```python
</pre></a>
        
<a name=63><pre>    from computerwords.cwdom.traversal import find_ancestor
</pre></a>
        
<a name=64><pre>    document_node = find_ancestor(node, lambda n: n.name == 'Document')
</pre></a>
        
<a name=65><pre>    ```
</pre></a>
        
<a name=66><pre>    """
</pre></a>
        
<a name=67><pre>    for ancestor in iterate_ancestors(node):
</pre></a>
        
<a name=68><pre>        if predicate(ancestor):
</pre></a>
        
<a name=69><pre>            return ancestor
</pre></a>
        
<a name=70><pre>
</pre></a>
        
<a name=71><pre>
</pre></a>
        
<a name=72><pre>def visit_tree(tree, node_name_to_visitor, node=None):
</pre></a>
        
<a name=73><pre>    """
</pre></a>
        
<a name=74><pre>    Recursively call the `CWTreeVisitor` for each node. If a node
</pre></a>
        
<a name=75><pre>    is encountered that has no corresponding visitor, `MissingVisitorError` is
</pre></a>
        
<a name=76><pre>    thrown.
</pre></a>
        
<a name=77><pre>
</pre></a>
        
<a name=78><pre>    ```python
</pre></a>
        
<a name=79><pre>    from computerwords.cwdom.CWTree import CWTree
</pre></a>
        
<a name=80><pre>    from computerwords.cwdom.traversal import (
</pre></a>
        
<a name=81><pre>        visit_tree,
</pre></a>
        
<a name=82><pre>        CWTreeVisitor
</pre></a>
        
<a name=83><pre>    )
</pre></a>
        
<a name=84><pre>
</pre></a>
        
<a name=85><pre>    visits = []
</pre></a>
        
<a name=86><pre>    class SimpleVisitor(CWTreeVisitor):
</pre></a>
        
<a name=87><pre>        def before_children(self, tree, node):
</pre></a>
        
<a name=88><pre>            visits.append('pre-{}'.format(node.name))
</pre></a>
        
<a name=89><pre>
</pre></a>
        
<a name=90><pre>        def after_children(self, tree, node):
</pre></a>
        
<a name=91><pre>            visits.append('post-{}'.format(node.name))
</pre></a>
        
<a name=92><pre>
</pre></a>
        
<a name=93><pre>    tree = CWTree(CWNode('x', [CWNode('y', [])]))
</pre></a>
        
<a name=94><pre>    visit_tree(tree, {
</pre></a>
        
<a name=95><pre>        'x': SimpleVisitor(),
</pre></a>
        
<a name=96><pre>        'y': SimpleVisitor(),
</pre></a>
        
<a name=97><pre>    })
</pre></a>
        
<a name=98><pre>    assert visits == ['pre-x', 'pre-y', 'post-y', 'post-x']
</pre></a>
        
<a name=99><pre>    ```
</pre></a>
        
<a name=100><pre>    """
</pre></a>
        
<a name=101><pre>    node = node or tree.root
</pre></a>
        
<a name=102><pre>    try:
</pre></a>
        
<a name=103><pre>        visitor = node_name_to_visitor[node.name]
</pre></a>
        
<a name=104><pre>    except KeyError:
</pre></a>
        
<a name=105><pre>        raise MissingVisitorError(
</pre></a>
        
<a name=106><pre>            "No visitor registered for {!r}".format(node.name))
</pre></a>
        
<a name=107><pre>    visitor.before_children(tree, node)
</pre></a>
        
<a name=108><pre>    for child in node.children:
</pre></a>
        
<a name=109><pre>        visit_tree(tree, node_name_to_visitor, child)
</pre></a>
        
<a name=110><pre>    visitor.after_children(tree, node)
</pre></a>
        
<a name=111><pre>
</pre></a>
        
<a name=112><pre>
</pre></a>
        
<a name=113><pre>class MissingVisitorError(Exception):
</pre></a>
        
<a name=114><pre>    """
</pre></a>
        
<a name=115><pre>    Error thrown when trying to visit a node for which no visitor is available.
</pre></a>
        
<a name=116><pre>    """
</pre></a>
        
<a name=117><pre>
</pre></a>
        
<a name=118><pre>
</pre></a>
        
<a name=119><pre>class CWTreeVisitor:
</pre></a>
        
<a name=120><pre>    def before_children(self, tree, node):
</pre></a>
        
<a name=121><pre>        """Called before the node's children are visited."""
</pre></a>
        
<a name=122><pre>
</pre></a>
        
<a name=123><pre>    def after_children(self, tree, node):
</pre></a>
        
<a name=124><pre>        """Called after the node's children are visited."""
</pre></a>
        
<a name=125><pre>
</pre></a>
        
<a name=126><pre>
</pre></a>
        
<a name=127><pre>class PostorderTraverser:
</pre></a>
        
<a name=128><pre>    """
</pre></a>
        
<a name=129><pre>    A class that lets you iterate over a tree while mutating it.
</pre></a>
        
<a name=130><pre>
</pre></a>
        
<a name=131><pre>    Keeps track of a *cursor* representing the last visited node. Each time
</pre></a>
        
<a name=132><pre>    the next node is requested, the iterator looks at the cursor and walks
</pre></a>
        
<a name=133><pre>    up the tree to find the cursor's next sibling or parent.
</pre></a>
        
<a name=134><pre>
</pre></a>
        
<a name=135><pre>    You may replace the cursor if you want to replace the node currently being
</pre></a>
        
<a name=136><pre>    visited.
</pre></a>
        
<a name=137><pre>
</pre></a>
        
<a name=138><pre>    You may safely mutate the cursor's ancestors, since they haven't been
</pre></a>
        
<a name=139><pre>    visited yet.
</pre></a>
        
<a name=140><pre>    """
</pre></a>
        
<a name=141><pre>
</pre></a>
        
<a name=142><pre>    def __init__(self, node):
</pre></a>
        
<a name=143><pre>        super().__init__()
</pre></a>
        
<a name=144><pre>        self.cursor = node
</pre></a>
        
<a name=145><pre>        self._is_first_result = True
</pre></a>
        
<a name=146><pre>
</pre></a>
        
<a name=147><pre>    def replace_cursor(self, new_cursor):
</pre></a>
        
<a name=148><pre>        """Only use this if you really know what you are doing."""
</pre></a>
        
<a name=149><pre>        self.cursor = new_cursor
</pre></a>
        
<a name=150><pre>
</pre></a>
        
<a name=151><pre>    def __iter__(self):
</pre></a>
        
<a name=152><pre>        return self
</pre></a>
        
<a name=153><pre>
</pre></a>
        
<a name=154><pre>    def __next__(self) -> "CWNode":
</pre></a>
        
<a name=155><pre>        if self._is_first_result:
</pre></a>
        
<a name=156><pre>            self._descend()
</pre></a>
        
<a name=157><pre>            self._is_first_result = False
</pre></a>
        
<a name=158><pre>        else:
</pre></a>
        
<a name=159><pre>            parent = self.cursor.get_parent()
</pre></a>
        
<a name=160><pre>            if not parent:
</pre></a>
        
<a name=161><pre>                raise StopIteration()
</pre></a>
        
<a name=162><pre>
</pre></a>
        
<a name=163><pre>            child_i = parent.children.index(self.cursor)
</pre></a>
        
<a name=164><pre>            next_child_i = child_i + 1
</pre></a>
        
<a name=165><pre>            if next_child_i >= len(parent.children):
</pre></a>
        
<a name=166><pre>                self.cursor = parent
</pre></a>
        
<a name=167><pre>            else:
</pre></a>
        
<a name=168><pre>                self.cursor = parent.children[next_child_i]
</pre></a>
        
<a name=169><pre>                self._descend()
</pre></a>
        
<a name=170><pre>        return self.cursor
</pre></a>
        
<a name=171><pre>
</pre></a>
        
<a name=172><pre>    def _descend(self):
</pre></a>
        
<a name=173><pre>        while self.cursor.children:
</pre></a>
        
<a name=174><pre>            self.cursor = self.cursor.children[0]
</pre></a>
        
    </body>
</html>
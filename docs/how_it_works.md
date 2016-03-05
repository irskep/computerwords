# How it works

## Input

First, your files are parsed into a tree called the “Computer Words Document
Object Model”, or `CWDOM`. So this:

```markdown filename=readme.md
# Title

some text
```

becomes this:

```graphviz-dot-convert
strict digraph {
    Root [label="Root" fontname="Helvetica" fontsize=10 shape="box"]
    Document [label="Document(path='readme.md')" fontname="Helvetica" fontsize=10 shape="box"]
    TitleText [label="Text(text='Title')" fontname="Helvetica" fontsize=10 shape="box"]
    BodyText [label="Text(text='some text')" fontname="Helvetica" fontsize=10 shape="box"]
    h1 [fontname="Helvetica" fontsize=10 shape="box"]
    p [fontname="Helvetica" fontsize=10 shape="box"]

    Root -> Document
    Document -> h1
    h1 -> TitleText
    Document -> p
    p -> BodyText
}
```

## Processing

Then we apply a processor library to the graph. A *library* is a mapping of
`node_name -> [processor]`. A *processor* is a function like this:

```python
@library.processor('xxx')  # operate on 'xxx' nodes
def process_xxx(node_store, node)
    # you can mutate the node, its children, or its
    # ancestors (but not its siblings).
    # In this case, we are swapping the node in place for
    # another node, which will have the original node's
    # parent and children.
    node_store.replace_node(node, CWDOMNode('yyy'))
```

Each node will be processed at least once, in a *post-order tree traversal*
(meaning that a node will be visited before its ancestors). If a node is
mutated by another node's processor, that node will be marked *dirty* and
its processors will be run again.

## Output

The *html writer* walks the tree and writes HTML.
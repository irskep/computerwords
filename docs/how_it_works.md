# How it works

## Read the config

First, Computer Words reads your config file, which tells it which Markdown
files you want to include, and in what order. See
[Defining table of contents structure with file_hierarchy](configuration.html#Defining-table-of-contents-structure-with-file_hierarchy)
for details

## Parse the Markdown files

Then, each file is parsed into a tree, with a `CWDocumentNode` as the root.
These document nodes are then added to a global `CWRootNode`.

Each node has a globally unique ID and a *name* (i.e. type, kind, label).

So this:

```markdown filename=readme.md
# Title

some text
```

```markdown filename=part2.md
# Part 2

text of part 2
```

becomes this:

```graphviz-simple
    Root [label="Root"]
    Document [label="Document(path='readme.md')"]
    TitleText [label="Text(text='Title')"]
    BodyText [label="Text(text='some text')"]

    Root -> Document
    Document -> h1
    h1 -> TitleText
    Document -> p
    p -> BodyText

    Document2 [label="Document(path='part2.md')"]
    h1b [label="h1"]
    TitleText2 [label="Text(text='Part 2')"]
    p2 [label="p"]
    BodyText2 [label="Text(text='text of part 2')"]

    Root -> Document2
    Document2 -> h1b
    h1b -> TitleText2
    Document2 -> p2
    p2 -> BodyText2
```

This is all stored in a `CWTree` object, which allows you to access and mutate
the tree in the next step.

## Processing

Then we apply a processor library to the graph. A *library* is a mapping of
`node_name -> [processor]`. A *processor* is a function `process(tree, node)`
which mutates the `tree` in response to visiting `node`.

For example, here's a processor that reverses all text:

```py
@library.processor('Text')
def reverse_text(tree, node):
    tree.replace_node(node, CWTextNode(node.text[::-1]))
```

The library is applied by traversing the tree in post-order (children before
parents). That way, when a node is visited, its subtree is guaranteed to be
complete.

If a processor mutates a child of its node, that node is marked "dirty". After
each post-order traversal of the whole tree, if any nodes are dirty, the tree
is traversed again, and only the dirty nodes' processors will be run.

Supported mutations are documented on
[`CWTree`](API.html#computerwords.cwdom.CWTree.CWTree).

## Output

Once the processors have been run until there are no more dirty nodes, it's
time to do something with the complete tree.

This is where a *writer* takes over. The job of a writer is to turn a
`CWTree` into human-readable output of some kind.

The only writer available right now is the HTML writer. It works by defining
a *visitor* for each node name, where each visitor writes the opening tag,
visits its children, and then writes the closing tag.

Since few people will be writing writers, this is the least well documented
part of Computer Words right now.

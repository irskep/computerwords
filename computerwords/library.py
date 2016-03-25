class UnhandledEdgeCaseError(Exception): pass
class UnknownNodeNameError(Exception): pass


class Library:
    """
    A collection of functions that can be applied to nodes. Each function is
    called a *processor* and applies to nodes with the given *name*.

    As a user of Computer Words, you really only need to know about the
    `processor()` method.
    """

    def __init__(self):
        super().__init__()
        self.tag_name_to_processors = {}
        self.universal_processors = []

    def _set_processor(self, tag_name, p, before_others=False):
        if tag_name == '*':
            if before_others:
                self.universal_processors.insert(0, p)
            else:
                self.universal_processors.append(p)
        else:
            self.tag_name_to_processors.setdefault(tag_name, [])
            if before_others:
                self.tag_name_to_processors[tag_name].insert(0, p)
            else:
                self.tag_name_to_processors[tag_name].append(p)

    def processor(self, tag_name, p=None, before_others=False):
        """
        Declare a function as a processor for nodes with name *tag_name*.
        May be used as a decorator or as a simple function call.

        As a decorator:

        ```py
        @library.processor('Text')
        def reverse_text(tree, node):
            tree.replace_node(node, CWTextNode(node.text[::-1]))
        ```

        As a function:

        ```py
        def reverse_text(tree, node):
            tree.replace_node(node, CWTextNode(node.text[::-1]))
        library.processor('Text', reverse_text)
        ```
        """
        if p is None:
            def decorator(p2):
                self._set_processor(tag_name, p2, before_others)
                return p2
            return decorator
        else:
            self._set_processor(tag_name, p, before_others)
            return p

    def get_processors(self, tag_name, strict=True):
        yield from self.universal_processors
        if strict:
            try:
                yield from self.tag_name_to_processors[tag_name]
            except KeyError:
                msg = (
                    "No processors are defined for nodes with name {!r}."
                ).format(tag_name)
                raise UnknownNodeNameError(msg)
        else:
            yield from self.tag_name_to_processors.get(tag_name, [])

    def get_allowed_tags(self):
        return set(self.tag_name_to_processors.keys())

    def run_processors(self, tree, node):
        if tree.get_is_node_dirty(node):
            raise ValueError(
                "Nodes should be marked un-dirty before processing.")
        for p in self.get_processors(node.name):
            if tree.get_is_node_dirty(node):
                raise UnhandledEdgeCaseError((
                    "Node {!r} has multiple processors, but an earlier"
                    " processor dirtied it before the later one could run."
                    " I haven't decided if this is a problem or not, so for"
                    " now this edge case simply throws an error.").format(
                        node.name))
            if tree.get_was_node_removed(node):
                return
                raise UnhandledEdgeCaseError((
                    "Node {!r} has multiple processors, but an earlier"
                    " processor removed it before the later one could run."
                    " I haven't decided if this is a problem or not, so for"
                    " now this edge case simply throws an error.").format(
                        node.name))
            p(tree, node)

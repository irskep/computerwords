class UnhandledEdgeCaseError(Exception): pass
class UnknownNodeNameError(Exception): pass


class Library:
    def __init__(self):
        super().__init__()
        self.tag_name_to_processors = {}

    def _set_processor(self, tag_name, p, before_others=False):
        self.tag_name_to_processors.setdefault(tag_name, [])
        if before_others:
            self.tag_name_to_processors[tag_name].insert(0, p)
        else:
            self.tag_name_to_processors[tag_name].append(p)

    # this is a decorator or a normal function
    def processor(self, tag_name, p=None, before_others=False):
        if p is None:
            def decorator(p2):
                self._set_processor(tag_name, p2, before_others)
                return p2
            return decorator
        else:
            self._set_processor(tag_name, p, before_others)
            return p

    def get_processors(self, tag_name, strict=True):
        if strict:
            try:
                return self.tag_name_to_processors[tag_name]
            except KeyError:
                msg = (
                    "No processors are defined for nodes with name {!r}."
                ).format(tag_name)
                raise UnknownNodeNameError(msg)
        else:
            return self.tag_name_to_processors.get(tag_name, [])

    def get_allowed_tags(self):
        return set(self.tag_name_to_processors.keys())

    def run_processors(self, node_store, node):
        for p in self.get_processors(node.name):
            if node_store.get_is_node_dirty(node):
                raise UnhandledEdgeCaseError((
                    "Node {!r} has multiple processors, but an earlier"
                    " processor dirtied it before the later one could run."
                    " I haven't decided if this is a problem or not, so for"
                    " now this edge case simply throws an error.").format(
                        node.name))
            if node_store.get_was_node_removed(node):
                raise UnhandledEdgeCaseError((
                    "Node {!r} has multiple processors, but an earlier"
                    " processor removed it before the later one could run."
                    " I haven't decided if this is a problem or not, so for"
                    " now this edge case simply throws an error.").format(
                        node.name))
            p(node_store, node)

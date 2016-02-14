from computerwords.cwdom.CWDOMNode import CWDOMEndOfInputNode


class UnhandledEdgeCaseError(Exception): pass


class Library:
    def __init__(self):
        super().__init__()
        self.tag_name_to_processors = {}

    def _set_processor(self, tag_name, p):
        self.tag_name_to_processors.setdefault(tag_name, [])
        self.tag_name_to_processors[tag_name].append(p)

    # this is a decorator or a normal function
    def processor(self, tag_name, p=None):
        if p is None:
            def decorator(p2):
                self._set_processor(tag_name, p2)
                return p2
            return decorator
        else:
            self._set_processor(tag_name, p)
            return p

    def get_processors(self, tag_name, strict=True):
        if strict:
            return self.tag_name_to_processors[tag_name]
        else:
            return self.tag_name_to_processors.get(tag_name, [])

    def get_allowed_tags(self):
        return set(self.tag_name_to_processors.keys())

    def run_processors(self, node_store, node):
        for p in self.get_processors(node.name):
            if node_store.get_is_node_invalid(node):
                raise UnhandledEdgeCaseError(
                    "Node has multiple processors, but an earlier processor"
                    " invalidated it before the later one could run."
                    " I haven't decided if this is a problem or not, so for"
                    " now this edge case simply throws an error.")
            if not node_store.get_is_node_still_in_tree(node):
                raise UnhandledEdgeCaseError(
                    "Node has multiple processors, but an earlier processor"
                    " removed it before the later one could run."
                    " I haven't decided if this is a problem or not, so for"
                    " now this edge case simply throws an error.")
            p(node_store, node)

    ### convenience methods for end node ###
    # (same as using CWDOMEndOfInputNode.NAME, but that's not very easy
    # to remember)

    # declare a function to run at the end of all input
    def end_processor(self, tag_name, p=None):
        return self.processor(CWDOMEndOfInputNode.NAME, p)

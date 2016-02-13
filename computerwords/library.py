from computerwords.cwdom.CWDOMNode import CWDOMEndOfInputNode


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

    # declare a function to run at the end of all input
    def end_processor(self, tag_name, p=None):
        return self.processor(CWDOMEndOfInputNode.NAME, p)

    def get_processors(self, tag_name, strict=True):
        if strict:
            return self.tag_name_to_processors[tag_name]
        else:
            return self.tag_name_to_processors.get(tag_name, [])

    def get_allowed_tags(self):
        return set(self.tag_name_to_processors.keys())

    def process_node(self, node_store, node):
        for p in self.get_processors(node.name):
            # TODO: handle node_store mutations inside this loop
            p(node_store, node)

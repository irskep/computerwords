TAG_NAME_TO_PROCESSORS = {}


def _set_processor(tag_name, p):
    TAG_NAME_TO_PROCESSORS.setdefault(tag_name, [])
    TAG_NAME_TO_PROCESSORS[tag_name].append(p)


def processor(tag_name, p=None):
    if p is None:
        def decorator(p2):
            _set_processor(tag_name, p2)
            return p2
        return decorator
    else:
        _set_processor(tag_name, p)
        return p


def get_processors(tag_name):
    return TAG_NAME_TO_PROCESSORS.get(tag_name, [])


def get_tag_names():
    return set(TAG_NAME_TO_PROCESSORS.keys())


def process_node(node_store, node):
    for p in get_processors(node.name):
        # TODO: handle node_store mutations inside this loop
        p(node_store, node)

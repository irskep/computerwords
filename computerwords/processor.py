TAG_NAME_TO_PROCESSORS = {}


def processor(tag_name, p=None):
    if p is None:
        def decorator(p2):
            TAG_NAME_TO_PROCESSORS.setdefault(tag_name, [])
            TAG_NAME_TO_PROCESSORS[tag_name].append(p2)
            return p2
        return decorator
    else:
        TAG_NAME_TO_PROCESSORS.setdefault(tag_name, [])
        TAG_NAME_TO_PROCESSORS[tag_name].append(p)
        return p


def get_processors(tag_name):
    return TAG_NAME_TO_PROCESSORS.get(tag_name, [])


def get_tag_names():
    return set(TAG_NAME_TO_PROCESSORS.viewkeys())


def process_node(node_store, node):
    for p in get_processors(node.name):
        # TODO: handle node_store mutations inside this loop
        p(node_store, node)

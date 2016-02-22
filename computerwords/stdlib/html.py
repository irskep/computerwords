def add_html(library):
    library.HTML_TAGS = {
        'strong', 'i', 'u', 's', 'tt', 'span', 'pre',
        'p', 'div',
        'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
        'ol', 'ul', 'li'
    }

    library.ALIAS_HTML_TAGS = {
        'strike': 's',
        'b': 'strong',
        'code': 'pre',
    }

    noop = lambda *args, **kwargs: None
    for html_tag in library.HTML_TAGS:
        library.processor(html_tag, noop)

    def define_alias(from_tag_name, to_tag_name):
        @library.processor(from_tag_name)
        def process_alias(node_store, node):
            # it's not strictly necessary to do the copy/replace in this
            # implementation, but if someone has added a processor to the
            # target tag name, we want that processor to run in another pass.
            node_store.replace_node(node, node.copy(name=to_tag_name))

    for from_tag_name, to_tag_name in library.ALIAS_HTML_TAGS.items():
        define_alias(from_tag_name, to_tag_name)

    @library.processor('a')
    def process_a(node_store, node):
        # the fanciest no-op...
        if 'href' in node.kwargs:
            return  # plain HTML reference
        elif 'name' in node.kwargs:
            return  # might do something with this later
        else:
            return

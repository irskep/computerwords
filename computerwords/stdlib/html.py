def add_html(library):
    library.HTML_TAGS = {
        'strong', 'i', 'u', 's', 'tt', 'span', 'pre',
        'p', 'div',
        'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
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
            node_store.replace(node, node.copy(name=to_tag_name))

    for from_tag_name, to_tag_name in library.ALIAS_HTML_TAGS.items():
        define_alias(from_tag_name, to_tag_name)

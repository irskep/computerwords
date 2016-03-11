from computerwords.cwdom.nodes import CWTagNode, CWTextNode


def add_html(library):
    library.SEMANTIC_HTML_TAGS = {
        'main', 'header', 'footer', 'article', 'section', 'aside', 'nav',
        'figure', 'figcaption'
    }

    library.HTML_TAGS = {
        'strong', 'i', 'u', 's', 'tt', 'span', 'pre',
        'p', 'div', 'a', 'br', 'hr',
        'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
        'ol', 'ul', 'li',
        'blockquote', 'img',

        'table', 'thead', 'tbody', 'tr', 'th', 'td', 'caption',
    } | library.SEMANTIC_HTML_TAGS

    library.ALIAS_HTML_TAGS = {
        'strike': 's',
        'b': 'strong',
        'code': 'pre',
    }

    all_tags = (
        library.SEMANTIC_HTML_TAGS |
        library.HTML_TAGS |
        library.ALIAS_HTML_TAGS.keys())

    noop = lambda *args, **kwargs: None
    for html_tag in library.HTML_TAGS:
        library.processor(html_tag, noop)

    def define_alias(from_tag_name, to_tag_name):
        @library.processor(from_tag_name)
        def process_alias(tree, node):
            # it's not strictly necessary to do the copy/replace in this
            # implementation, but if someone has added a processor to the
            # target tag name, we want that processor to run in another pass.
            tree.replace_node(node, node.copy(name=to_tag_name))

    for from_tag_name, to_tag_name in library.ALIAS_HTML_TAGS.items():
        define_alias(from_tag_name, to_tag_name)

    @library.processor('a')
    def process_a(tree, node):
        # the fanciest no-op...
        if 'href' in node.kwargs:
            return  # plain HTML reference
        elif 'name' in node.kwargs:
            return  # might do something with this later
        else:
            return

    @library.processor('html-enumerate-all-tags')
    def process_enumerate_all_tags(tree, node):
        tree.replace_subtree(node, CWTagNode('tt', {}, [
            CWTextNode(', '.join(sorted(all_tags)))
        ]))

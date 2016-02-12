from computerwords.library import Library


class StandardLibrary(Library):
    HTML_TAGS = {
        'strong', 'i', 'u', 's', 'tt', 'span',
        'p', 'div',
        'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
    }

    ALIAS_HTML_TAGS = {
        'strike': 's',
        'b': 'strong',
    }

stdlib = StandardLibrary()


# Many tags require no processing
passthrough = lambda *args, **kwargs: None


stdlib.processor('Root', passthrough)
stdlib.processor('Text', passthrough)



for html_tag in stdlib.HTML_TAGS:
    stdlib.processor(html_tag, passthrough)


def define_alias(from_tag_name, to_tag_name):
    @stdlib.processor(from_tag_name)
    def process_alias(node_store, node):
        node_store.replace(node, node.copy(name=to_tag_name))


for from_tag_name, to_tag_name in stdlib.ALIAS_HTML_TAGS.items():
    define_alias(from_tag_name, to_tag_name)

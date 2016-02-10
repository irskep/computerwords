from computerwords.processor import processor


# Many tags require no processing
passthrough = lambda *args, **kwargs: None


HTML_TAGS = {
    'b', 'i', 'u', 's', 'tt', 'span',
    'p', 'div',
    'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
}


for html_tag in HTML_TAGS:
    processor(html_tag, passthrough)


ALIAS_HTML_TAGS = {
    'strike': 's'
}


for from_tag_name, to_tag_name in ALIAS_HTML_TAGS.items():
    @processor(from_tag_name)
    def process_alias(node_store, node):
        node_store.replace(node, node.copy(name=name))

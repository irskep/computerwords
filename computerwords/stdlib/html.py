from computerwords.cwdom.nodes import CWTagNode, CWTextNode


def add_html(library):
    SEMANTIC_HTML_TAGS = {
        'main', 'header', 'footer', 'article', 'section', 'aside', 'nav',
        'figure', 'figcaption', 'address', 'hgroup',

        'details', 'dialog', 'menu', 'menuitem', 'summary',
    }

    BLOCK_LEVEL_TAGS = {
        'pre', 'p', 'div', 'hr',
        'ol', 'ul', 'li',
        'blockquote',
        'canvas', 'script', 'noscript'
    }

    MEDIA_TAGS = {
        'map', 'area',
        'audio', 'track', 'video',
    }

    HEADING_TAGS = {
        'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
    }

    INLINE_TAGS = {
        'strong', 'i', 'u', 's', 'span', 'code',
        'a', 'br', 'img',
        'abbr', 'bdi', 'bdo', 'cite', 'data', 'dfn', 'em', 'kbd', 'mark',
        'q', 'samp', 'small', 'sub', 'sup', 'time', 'var', 'wbr',
        'del', 'ins',

        'rp', 'rt', 'rtc', 'ruby',
    }

    TABLE_TAGS = {
        'table', 'thead', 'tbody', 'tr', 'th', 'td', 'caption', 'col',
        'colgroup', 'tfoot', 'thead',
    }

    DEFN_TAGS = {'dd', 'dl', 'dt'}

    EMBEDDING_TAGS = {'embed', 'object', 'param', 'source'}

    FORM_TAGS = {
        'button', 'datalist', 'fieldset', 'form', 'input', 'keygen', 'label',
        'legend', 'meter', 'optgroup', 'option', 'output', 'progress',
        'select',
    }

    EXPERIMENTAL_TAGS = {
        'content', 'element', 'shadow', 'template',
    }

    DEPRECATED_TAGS = {
        'acronym', 'applet', 'basefont', 'big', 'blink', 'center', 'command',
        'content', 'dir', 'font', 'frame', 'frameset', 'isindex', 'listing',
        'marquee', 'noembed', 'plaintext', 'spacer', 'xmp',
    }

    library.HTML_TAGS = (
        SEMANTIC_HTML_TAGS |
        BLOCK_LEVEL_TAGS |
        HEADING_TAGS |
        INLINE_TAGS |
        TABLE_TAGS |
        DEFN_TAGS |
        MEDIA_TAGS |
        EMBEDDING_TAGS |
        FORM_TAGS |
        EXPERIMENTAL_TAGS |
        DEPRECATED_TAGS
    )

    library.ALIAS_HTML_TAGS = {
        'strike': 's',
        'b': 'strong',
        'tt': 'code',
    }

    all_tags = (
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

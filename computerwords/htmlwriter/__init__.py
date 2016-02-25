from computerwords.cwdom.NodeStore import NodeStoreVisitor


class WritingVisitor(NodeStoreVisitor):
    def __init__(self, output_stream):
        super().__init__()
        self.output_stream = output_stream


class TagVisitor(WritingVisitor):
    def __init__(self, output_stream, tag_name):
        super().__init__(output_stream)
        self.tag_name = tag_name

    def before_children(self, node):
        args_str_items = []
        for k, v in node.kwargs.items():
            # TODO: escape the value properly
            args_str_items.append(" {}='{}'".format(k, v))
        self.output_stream.write('<{}{}>'.format(
            self.tag_name, ''.join(args_str_items)))

    def after_children(self, node):
        self.output_stream.write('</{}>'.format(self.tag_name))


class TextVisitor(WritingVisitor):
    def __init__(self, output_stream, tag_name):
        super().__init__(output_stream)
        self.tag_name = tag_name

    def before_children(self, node):
        self.output_stream.write(node.text)


class AnchorVisitor(WritingVisitor):
    def before_children(self, node):
        self.output_stream.write('<a name="{}">'.format(node.ref_id))

    def after_children(self, node):
        self.output_stream.write('</a>')


class LinkVisitor(WritingVisitor):
    def before_children(self, node):
        self.output_stream.write('<a href="#{}">'.format(node.ref_id))

    def after_children(self, node):
        self.output_stream.write('</a>')


class DocumentVisitor(WritingVisitor):
    def before_children(self, node):
        self.output_stream.write('<html><body>')

    def after_children(self, node):
        self.output_stream.write('</body></html>')


def cwdom_to_html_string(library, node_store, output_stream):
    tag_to_visitor = {
        tag: TagVisitor(output_stream, tag)
        for tag in library.HTML_TAGS | set(library.ALIAS_HTML_TAGS.keys())
    }
    tag_to_visitor['Root'] = NodeStoreVisitor()  # no-op
    tag_to_visitor['Document'] = DocumentVisitor(output_stream)
    tag_to_visitor['Text'] = TextVisitor(output_stream, 'Text')
    tag_to_visitor['Anchor'] = AnchorVisitor(output_stream)
    tag_to_visitor['Link'] = LinkVisitor(output_stream)
    node_store.visit_all(tag_to_visitor)
    output_stream.write('\n')

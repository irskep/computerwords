from computerwords.cwdom.NodeStore import NodeStoreVisitor


class TagVisitor(NodeStoreVisitor):
    def __init__(self, output_stream, tag_name):
        super().__init__()
        self.output_stream = output_stream
        self.tag_name = tag_name

    def before_children(self, node):
        self.output_stream.write('<{}>'.format(self.tag_name))

    def after_children(self, node):
        self.output_stream.write('</{}>'.format(self.tag_name))


class TextVisitor(NodeStoreVisitor):
    def __init__(self, output_stream, tag_name):
        super().__init__()
        self.output_stream = output_stream
        self.tag_name = tag_name

    def before_children(self, node):
        self.output_stream.write(node.text)


def cwdom_to_html_string(library, node_store, output_stream):
    tag_to_visitor = {
        tag: TagVisitor(output_stream, tag)
        for tag in library.get_allowed_tags()
    }
    tag_to_visitor['Root'] = NodeStoreVisitor()  # no-op
    tag_to_visitor['Text'] = TextVisitor(output_stream, 'Text')
    node_store.visit_all(tag_to_visitor)
    output_stream.write('\n')

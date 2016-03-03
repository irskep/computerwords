import html

from computerwords.cwdom.NodeStore import NodeStoreVisitor

from .util import (
    anchor_to_href,
    html_attrs_to_string,
)


def get_tag_to_visitor(library, stream, options):
    tag_to_visitor = {
        tag: TagVisitor(options, stream, tag)
        for tag in library.HTML_TAGS | set(library.ALIAS_HTML_TAGS.keys())
    }
    tag_to_visitor['Root'] = NodeStoreVisitor()  # no-op
    tag_to_visitor['Document'] = DocumentVisitor(options, stream)
    tag_to_visitor['Text'] = TextVisitor(options, stream, 'Text')
    tag_to_visitor['Anchor'] = AnchorVisitor(options, stream)
    tag_to_visitor['Link'] = LinkVisitor(options, stream)
    return tag_to_visitor


class WritingVisitor(NodeStoreVisitor):
    def __init__(self, options, output_stream):
        super().__init__()
        self.options = options
        self.output_stream = output_stream


class TagVisitor(WritingVisitor):
    def __init__(self, options, output_stream, tag_name):
        super().__init__(options, output_stream)
        self.tag_name = tag_name

    def before_children(self, node_store, node):
        self.output_stream.write('<{}{}>'.format(
            self.tag_name, html_attrs_to_string(node.kwargs)))

    def after_children(self, node_store, node):
        self.output_stream.write('</{}>'.format(self.tag_name))


class TextVisitor(WritingVisitor):
    def __init__(self, options, output_stream, tag_name):
        super().__init__(options, output_stream)
        self.tag_name = tag_name

    def before_children(self, node_store, node):
        self.output_stream.write(html.escape(node.text))


class AnchorVisitor(WritingVisitor):
    def before_children(self, node_store, node):
        # just relative to itself
        href = anchor_to_href(self.options, node, node)
        self.output_stream.write('<a name="{}"{}>'.format(
            href, html_attrs_to_string(node.kwargs)))

    def after_children(self, node_store, node):
        self.output_stream.write('</a>')


class LinkVisitor(WritingVisitor):
    def before_children(self, node_store, node):
        href = anchor_to_href(
            self.options,
            node,
            node_store.processor_data['ref_id_to_anchor'][node.ref_id])
        self.output_stream.write('<a href="{}">'.format(href))

    def after_children(self, node_store, node):
        self.output_stream.write('</a>')


class DocumentVisitor(WritingVisitor):
    def before_children(self, node_store, node):
        self.output_stream.write('<article>')

    def after_children(self, node_store, node):
        if self.options.single_page:
            self.output_stream.write('<hr />')
        self.output_stream.write('</article>')


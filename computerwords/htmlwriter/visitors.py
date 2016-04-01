import html

from computerwords.cwdom.traversal import CWTreeVisitor

from .util import (
    anchor_to_href,
    doc_id_to_single_page_anchor_name,
    doc_to_href,
    html_attrs_to_string,
)


def get_tag_to_visitor(library, stream, options):
    tag_to_visitor = {
        tag: TagVisitor(options, stream, tag)
        for tag in library.HTML_TAGS | set(library.ALIAS_HTML_TAGS.keys())
    }
    tag_to_visitor['Root'] = CWTreeVisitor()  # no-op
    tag_to_visitor['Empty'] = CWTreeVisitor()  # no-op
    tag_to_visitor['Document'] = DocumentVisitor(options, stream)
    tag_to_visitor['Text'] = TextVisitor(options, stream, 'Text')
    tag_to_visitor['Anchor'] = AnchorVisitor(options, stream)
    tag_to_visitor['Link'] = LinkVisitor(options, stream)
    tag_to_visitor['DocumentLink'] = DocumentLinkVisitor(options, stream)
    return tag_to_visitor


class WritingVisitor(CWTreeVisitor):
    def __init__(self, options, output_stream):
        super().__init__()
        self.options = options
        self.output_stream = output_stream


class TagVisitor(WritingVisitor):
    def __init__(self, options, output_stream, tag_name):
        super().__init__(options, output_stream)
        self.tag_name = tag_name

    def before_children(self, tree, node):
        self.output_stream.write('<{}{}>'.format(
            self.tag_name, html_attrs_to_string(node.kwargs)))

    def after_children(self, tree, node):
        self.output_stream.write('</{}>'.format(self.tag_name))


class TextVisitor(WritingVisitor):
    def __init__(self, options, output_stream, tag_name):
        super().__init__(options, output_stream)
        self.tag_name = tag_name

    def before_children(self, tree, node):
        if node.escape:
            self.output_stream.write(html.escape(node.text))
        else:
            self.output_stream.write(node.text)


class AnchorVisitor(WritingVisitor):
    def before_children(self, tree, node):
        # just relative to itself
        name = anchor_to_href(self.options, node, node)
        fmt = '<a href="#{name}" name="{name}"{attrs}>'
        self.output_stream.write(fmt.format(
            name=name, attrs=html_attrs_to_string(node.kwargs)))

    def after_children(self, tree, node):
        self.output_stream.write('</a>')


class LinkVisitor(WritingVisitor):
    def before_children(self, tree, node):
        href = anchor_to_href(
            self.options,
            node,
            tree.processor_data['ref_id_to_anchor'][node.ref_id])
        self.output_stream.write('<a href="{}">'.format(href))

    def after_children(self, tree, node):
        self.output_stream.write('</a>')


class DocumentLinkVisitor(WritingVisitor):
    def before_children(self, tree, node):
        href = doc_to_href(self.options, node, node.target_document_id)
        self.output_stream.write('<a href="{}">'.format(href))

    def after_children(self, tree, node):
        self.output_stream.write('</a>')


class DocumentVisitor(WritingVisitor):
    def before_children(self, tree, node):
        if self.options.single_page:
            self.output_stream.write('<a name="{}">'.format(
                doc_id_to_single_page_anchor_name(node.document_id)))
        self.output_stream.write('<article>')

    def after_children(self, tree, node):
        if self.options.single_page:
            self.output_stream.write('<hr>')
        self.output_stream.write('</article>')
        if self.options.single_page:
            self.output_stream.write('</a>')


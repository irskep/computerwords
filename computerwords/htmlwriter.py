from io import StringIO
import pathlib

from computerwords.cwdom.NodeStore import NodeStoreVisitor


def _anchor_to_href(link_node, anchor_node):
    # in a multi-page world, we can omit the document part
    # if link_node.document_id == anchor_node.document_id.
    return "{}-{}".format(
        '/'.join(anchor_node.document_id), anchor_node.ref_id)


class WritingVisitor(NodeStoreVisitor):
    def __init__(self, output_stream):
        super().__init__()
        self.output_stream = output_stream


class TagVisitor(WritingVisitor):
    def __init__(self, output_stream, tag_name):
        super().__init__(output_stream)
        self.tag_name = tag_name

    def before_children(self, node_store, node):
        args_str_items = []
        for k, v in node.kwargs.items():
            # TODO: escape the value properly
            args_str_items.append(" {}='{}'".format(k, v))
        self.output_stream.write('<{}{}>'.format(
            self.tag_name, ''.join(args_str_items)))

    def after_children(self, node_store, node):
        self.output_stream.write('</{}>'.format(self.tag_name))


class TextVisitor(WritingVisitor):
    def __init__(self, output_stream, tag_name):
        super().__init__(output_stream)
        self.tag_name = tag_name

    def before_children(self, node_store, node):
        self.output_stream.write(node.text)


class AnchorVisitor(WritingVisitor):
    def before_children(self, node_store, node):
        # just relative to itself
        href = _anchor_to_href(node, node)
        self.output_stream.write('<a name="{}">'.format(href))

    def after_children(self, node_store, node):
        self.output_stream.write('</a>')


class LinkVisitor(WritingVisitor):
    def before_children(self, node_store, node):
        href = _anchor_to_href(
            node,
            node_store.processor_data['ref_id_to_anchor'][node.ref_id])
        self.output_stream.write('<a href="#{}">'.format(href))

    def after_children(self, node_store, node):
        self.output_stream.write('</a>')


class DocumentVisitor(WritingVisitor):
    def before_children(self, node_store, node):
        self.output_stream.write('<html><body>')

    def after_children(self, node_store, node):
        self.output_stream.write('</body></html>')


def write(config, input_files_root, output_files_root, library, node_store):
    print(config)
    print(input_files_root)
    print(output_files_root)

    static_dir = output_files_root / config['static_dir_name']
    static_dir.mkdir(exist_ok=True)

    stream = StringIO()
    tag_to_visitor = {
        tag: TagVisitor(stream, tag)
        for tag in library.HTML_TAGS | set(library.ALIAS_HTML_TAGS.keys())
    }
    tag_to_visitor['Root'] = NodeStoreVisitor()  # no-op
    tag_to_visitor['Document'] = DocumentVisitor(stream)
    tag_to_visitor['Text'] = TextVisitor(stream, 'Text')
    tag_to_visitor['Anchor'] = AnchorVisitor(stream)
    tag_to_visitor['Link'] = LinkVisitor(stream)
    node_store.visit_all(tag_to_visitor)

    module_dir = pathlib.Path(__file__).parent.resolve()

    css_files = [
        (module_dir / "_css" / "normalize.css", static_dir / "normalize.css")
    ]
    if config['css_files']:
        for path_str in config['css_files']:
            for path in input_files_root.glob(path_str):
                rel_path = path.relative_to(input_files)
                css_files.append((path, output_files_root.joinpath(rel_path)))

    for in_path, out_path in css_files:
        with in_path.open('r') as r:
            with out_path.open('w') as w:
                w.write(r.read())

    stylesheet_tag_strings = [
        '<link rel="stylesheet" href="{}" type="text/css" />'.format(
            p.relative_to(output_files_root))
        for _, p in css_files
    ]

    template_path = module_dir / "_html" / "single_page.html"
    output_path = output_files_root / "index.html"
    output_path.touch()
    with template_path.open('r') as template_stream:
        with output_path.open('w') as output_stream:
            output_stream.write(template_stream.read().format(
                stylesheet_tags="".join(stylesheet_tag_strings),
                body=stream.getvalue(),
                **config,
            ))



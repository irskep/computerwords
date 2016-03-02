import pathlib
from io import StringIO

import computerwords
from .visitors import *
from .util import (
    SINGLE_PAGE_TEMPLATE_PATH,
    copy_files,
    read_htmlwriter_options,
)


def write(config, input_dir, output_dir, library, node_store):
    options = read_htmlwriter_options(config, input_dir, output_dir)

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

    copy_files(options.files_to_copy)

    output_path = output_dir / "index.html"
    output_path.touch()
    with SINGLE_PAGE_TEMPLATE_PATH.open('r') as template_stream:
        with output_path.open('w') as output_stream:
            output_stream.write(template_stream.read().format(
                stylesheet_tags="".join(options.stylesheet_tag_strings),
                body=stream.getvalue(),
                **config,
            ))



import pathlib
from io import StringIO

import computerwords
from .visitors import get_tag_to_visitor
from .util import (
    SINGLE_PAGE_TEMPLATE_PATH,
    copy_files,
    read_htmlwriter_options,
)


def write(config, input_dir, output_dir, library, node_store):
    options = read_htmlwriter_options(config, input_dir, output_dir)

    stream = StringIO()
    node_store.visit_all(get_tag_to_visitor(library, stream, options))

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



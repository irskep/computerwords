import html
import pathlib
from collections import namedtuple

import computerwords


HTMLWriterOptions = namedtuple('HTMLWriterOptions', [
    'static_dir',
    'files_to_copy',
    'stylesheet_tag_strings',
])


MODULE_DIR = pathlib.Path(computerwords.__file__).parent.resolve()
NORMALIZE_CSS_PATH = MODULE_DIR / "_css" / "normalize.css"
SINGLE_PAGE_TEMPLATE_PATH = MODULE_DIR / "_html" / "single_page.html"


def anchor_to_href(link_node, anchor_node):
    # in a multi-page world, we can omit the document part
    # if link_node.document_id == anchor_node.document_id.
    return "{}-{}".format(
        '/'.join(anchor_node.document_id), anchor_node.ref_id)


def html_attrs_to_string(kwargs):
    args_str_items = []
    for k, v in kwargs.items():
        # TODO: escape the value properly
        args_str_items.append(" {}='{}'".format(k, v))
    return ''.join(args_str_items)


def copy_files(in_out_path_pairs):
    """Dumb way to copy files"""
    for in_path, out_path in in_out_path_pairs:
        with in_path.open('r') as r:
            with out_path.open('w') as w:
                w.write(r.read())


def read_htmlwriter_options(config, input_dir, output_dir):
    static_dir = output_dir / config['static_dir_name']
    static_dir.mkdir(exist_ok=True)

    css_theme = config['css_theme'] + ".css"
    css_files = [
        (NORMALIZE_CSS_PATH, static_dir / "normalize.css"),
        (MODULE_DIR / "_css" / css_theme, static_dir / css_theme),
    ]

    if config['css_files']:
        assert(isinstance(config['css_files'], list))
        for path_str in config['css_files']:
            for path in input_dir.glob(path_str):
                rel_path = path.relative_to(input_dir)
                css_files.append((path, output_dir.joinpath(rel_path)))

    files_to_copy = css_files

    stylesheet_tag_strings = [
        '<link rel="stylesheet" href="{}" type="text/css" />'.format(
            p.relative_to(output_dir))
        for _, p in css_files
    ]

    return HTMLWriterOptions(
        static_dir=static_dir,
        files_to_copy=files_to_copy,
        stylesheet_tag_strings=stylesheet_tag_strings)

import html
import os
import pathlib
from collections import namedtuple

from pygments.formatters import HtmlFormatter

import computerwords


HTMLWriterOptions = namedtuple('HTMLWriterOptions', [
    'single_page',
    'static_dir',
    'files_to_copy',
    'stylesheet_tag_strings',
    'site_url',
    'meta_description',
])


MODULE_DIR = pathlib.Path(computerwords.__file__).parent.resolve()
NORMALIZE_CSS_PATH = MODULE_DIR / "_css" / "normalize.css"
SINGLE_PAGE_TEMPLATE_PATH = MODULE_DIR / "_html" / "single_page.html"


def document_id_to_link_root(doc_id):
    return os.path.splitext('/'.join(doc_id))[0] + '.html'


def find_path_between(a, b):
    i = 0
    while i < len(a) and i < len(b) and a[i] == b[i]:
        i += 1
    a = a[i:]
    b = b[i:]
    num_dots = len(a) - 1
    path = '/'.join(['..'] * num_dots + list(b))
    if path:
        return path + '.html'
    else:
        return ''


def doc_to_href(options, link_node, target_doc_id):
    if options.single_page: return ''  # probably not used...
    if link_node.document_id == target_doc_id: return ''

    return find_path_between(link_node.document_id, target_doc_id)


def anchor_to_href(options, link_node, anchor_node):
    if options.single_page:
        name = "{}-{}".format(
                '/'.join(anchor_node.document_id), anchor_node.ref_id)
        if link_node is anchor_node:
            return name
        else:
            return '#' + name
    else:
        name = anchor_node.ref_id
        if link_node is anchor_node:
            return name
        else:
            return "{}#{}".format(
                find_path_between(link_node.document_id, anchor_node.document_id),
                anchor_node.ref_id)


def doc_id_to_single_page_anchor_name(doc_id):
    return 'doc-' + '-'.join(doc_id)


def html_attrs_to_string(kwargs):
    args_str_items = []
    for k, v in kwargs.items():
        # TODO: escape the value properly?
        args_str_items.append(" {}='{}'".format(k, v))
    return ''.join(args_str_items)


def copy_files(in_out_path_pairs):
    """Dumb way to copy files"""
    for in_path, out_path in in_out_path_pairs:
        with in_path.open('r') as r:
            with out_path.open('w') as w:
                w.write(r.read())


def read_htmlwriter_options(config, input_dir, output_dir):
    html_config = config.get('html', {})

    static_dir = output_dir / html_config.get('static_dir_name', 'static')
    static_dir.mkdir(exist_ok=True)

    css_theme = html_config.get('css_theme', 'default') + ".css"
    css_files = [
        (NORMALIZE_CSS_PATH, static_dir / "normalize.css"),
        (MODULE_DIR / "_css" / css_theme, static_dir / css_theme),
    ]

    if html_config['css_files']:
        assert(isinstance(html_config['css_files'], list))
        for path_str in html_config['css_files']:
            for path in input_dir.glob(path_str):
                rel_path = path.relative_to(input_dir)
                css_files.append((path, output_dir.joinpath(rel_path)))

    files_to_copy = [f for f in css_files]

    pygments_css_path = static_dir / "pygments.css"
    with pygments_css_path.open('w') as f:
        f.write(HtmlFormatter(style='tango').get_style_defs())

    css_files.append((None, pygments_css_path))

    stylesheet_tag_strings = [
        '<link rel="stylesheet" href="{}" type="text/css" />'.format(
            p.relative_to(output_dir))
        for _, p in css_files
    ]

    return HTMLWriterOptions(
        single_page=html_config.get('single_page', False),
        static_dir=static_dir,
        files_to_copy=files_to_copy,
        stylesheet_tag_strings=stylesheet_tag_strings,
        site_url=html_config.get('site_url', '/'),
        meta_description=html_config.get('meta_description', '/'),
    )

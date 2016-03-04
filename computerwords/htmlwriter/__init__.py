import pathlib
from io import StringIO

import computerwords  # to get the module root path
from computerwords.cwdom.CWDOMNode import CWDOMLinkNode, CWDOMTagNode, CWDOMTextNode
from .visitors import get_tag_to_visitor
from .util import (
    SINGLE_PAGE_TEMPLATE_PATH,
    copy_files,
    read_htmlwriter_options,
)


def write_single_page(config, options, output_dir, library, node_store):
    body = _get_subtree_html(config, options, library, node_store)

    output_path = output_dir / "index.html"
    output_path.touch()
    with SINGLE_PAGE_TEMPLATE_PATH.open('r') as template_stream:
        with output_path.open('w') as output_stream:
            output_stream.write(template_stream.read().format(
                nav_html='',
                stylesheet_tags="".join(options.stylesheet_tag_strings),
                body=body,
                **config,
            ))


def _get_subtree_html(config, options, library, node_store, node=None):
    stream = StringIO()
    node_store.visit_all(get_tag_to_visitor(library, stream, options), node)
    return stream.getvalue()


def _get_nav_html_part(
        config, options, library, node_store, document_node,
        entry_key, css_class, is_prev=False):
    if entry_key in document_node.data:
        entry = document_node.data[entry_key]
        ref_id = entry.ref_id
        if is_prev:
            node = CWDOMTagNode('nav', {'class': css_class}, [
                CWDOMLinkNode(ref_id, [
                    CWDOMTextNode('&larr; ', escape=False)
                ]).deepcopy_children_from(entry.heading_node, at_end=True)
            ])
        else:
            node = CWDOMTagNode('nav', {'class': css_class}, [
                CWDOMLinkNode(ref_id, [
                    CWDOMTextNode(' &rarr;', escape=False)
                ]).deepcopy_children_from(entry.heading_node)
            ])
        return _get_subtree_html(
            config, options, library, node_store, node)
    else:
        return ''


def write_document(config, options, output_dir, library, node_store, document_node):
    body = _get_subtree_html(config, options, library, node_store, document_node)

    output_path = output_dir
    for directory in document_node.document_id[:-1]:
        output_path = output_path / directory
    output_path = (output_path / document_node.document_id[-1]).with_suffix(".html")
    output_path.touch()

    nav_html = (
        _get_nav_html_part(
            config, options, library, node_store, document_node,
            'nav_previous_entry', 'previous-page', is_prev=True) +
        _get_nav_html_part(
            config, options, library, node_store, document_node,
            'nav_next_entry', 'next-page', is_prev=False))

    nav_next_node = None
    if 'nav_previous_entry' in document_node.data:
        entry = document_node.data['nav_previous_entry']
        ref_id = entry.ref_id
        nav_prev_node = CWDOMLinkNode(ref_id).deepcopy_children_from(entry.heading_node)
    with SINGLE_PAGE_TEMPLATE_PATH.open('r') as template_stream:
        with output_path.open('w') as output_stream:
            output_stream.write(template_stream.read().format(
                stylesheet_tags="".join(options.stylesheet_tag_strings),
                body=body,
                nav_html=nav_html,
                html_options=options,
                **config,
            ))


def write_multi_page(config, options, output_dir, library, node_store):
    for document_node in node_store.root.children:
        write_document(config, options, output_dir, library, node_store, document_node)


def write(config, input_dir, output_dir, library, node_store):
    options = read_htmlwriter_options(config, input_dir, output_dir)

    copy_files(options.files_to_copy)

    if options.single_page:
        write_single_page(config, options, output_dir, library, node_store)
    else:
        write_multi_page(config, options, output_dir, library, node_store)

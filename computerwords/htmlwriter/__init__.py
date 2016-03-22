import pathlib
from io import StringIO

import computerwords  # to get the module root path
from computerwords.cwdom.nodes import (
    CWDocumentLinkNode,
    CWTagNode,
    CWTextNode,
)
from computerwords.cwdom.traversal import visit_tree, preorder_traversal
from .visitors import get_tag_to_visitor
from .util import (
    SINGLE_PAGE_TEMPLATE_PATH,
    copy_files,
    doc_to_href,
    read_htmlwriter_options,
)


def _get_subtree_html(config, options, library, tree, node=None):
    stream = StringIO()
    visit_tree(tree, get_tag_to_visitor(library, stream, options), node)
    return stream.getvalue()


def _get_nav_html_part(
        config, options, library, tree, document_node, is_prev=False):
    entry_key = 'nav_previous_entry' if is_prev else 'nav_next_entry'
    if entry_key not in document_node.data:
        return ''

    entry = document_node.data[entry_key]
    ref_id = entry.ref_id
    if is_prev:
        css_class = 'previous-page'
        text = CWTextNode('&larr; ', escape=False)
    else:
        css_class = 'next-page'
        text = CWTextNode(' &rarr;', escape=False)

    node = CWTagNode('nav', {'class': css_class}, [
        CWDocumentLinkNode(entry.heading_node.document_id, [
            text
        ]).deepcopy_children_from(entry.heading_node, at_end=is_prev)
    ])
    node.deep_set_document_id(document_node.document_id)
    return _get_subtree_html(config, options, library, tree, node)


def write_document(config, options, output_dir, library, tree, document_node):
    body = _get_subtree_html(config, options, library, tree, document_node)

    output_path = output_dir
    for directory in document_node.document_id[:-1]:
        output_path = output_path / directory
    output_path = (output_path / document_node.document_id[-1]).with_suffix(".html")
    output_path.touch()

    nav_html = (
        _get_nav_html_part(
            config, options, library, tree, document_node, is_prev=True) +
        _get_nav_html_part(
            config, options, library, tree, document_node, is_prev=False))


    ctx = {k: v for k, v in config.items()}
    if not options.single_page:
        relative_site_url = doc_to_href(
            options,
            document_node,
            tree.processor_data['toc'][0][0].heading_node.document_id)
        ctx['title_url'] = relative_site_url
    else:
        ctx['title_url'] = options.site_url

    ctx['page_title'] = ctx['site_subtitle']
    for node in preorder_traversal(document_node):
        if node.name == 'h1':
            ctx['page_title'] = tree.subtree_to_text(node)
            break

    ctx['site_title_with_version'] = (
        ctx['site_title'] if ctx['project_version'] is None else
        '{} <span class="project-version">{}</span>'.format(
            ctx['site_title'], ctx['project_version'] ))

    with SINGLE_PAGE_TEMPLATE_PATH.open('r') as template_stream:
        with output_path.open('w') as output_stream:
            output_stream.write(template_stream.read().format(
                stylesheet_tags="".join(options.stylesheet_tag_strings),
                body=body,
                nav_html=nav_html,
                html_options=options,
                **ctx,
            ))


def write_multi_page(config, options, output_dir, library, tree):
    for document_node in tree.root.children:
        write_document(config, options, output_dir, library, tree, document_node)


def write_single_page(config, options, output_dir, library, tree):
    body = _get_subtree_html(config, options, library, tree)

    output_path = output_dir / "index.html"
    output_path.touch()

    ctx = {k: v for k, v in config.items()}
    ctx['site_title_with_version'] = (
        ctx['site_title'] if ctx['project_version'] is None else
        '{} <span class="project-version">{}</span>'.format(
            ctx['site_title'], ctx['project_version'] ))

    with SINGLE_PAGE_TEMPLATE_PATH.open('r') as template_stream:
        with output_path.open('w') as output_stream:
            output_stream.write(template_stream.read().format(
                nav_html='',
                stylesheet_tags="".join(options.stylesheet_tag_strings),
                body=body,
                html_options=options,
                **ctx,
            ))


def write(config, input_dir, output_dir, library, tree):
    options = read_htmlwriter_options(config, input_dir, output_dir)

    copy_files(options.files_to_copy)

    if options.single_page:
        write_single_page(config, options, output_dir, library, tree)
    else:
        write_multi_page(config, options, output_dir, library, tree)

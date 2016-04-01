import logging

from computerwords.plugin import CWPlugin

from computerwords.cwdom.nodes import CWEmptyNode, CWLinkNode
from computerwords.cwdom.traversal import find_ancestor, preorder_traversal


log = logging.getLogger(__name__)


class HeadingAliasesPlugin(CWPlugin):

    def add_processors(self, library):

        def init(tree):
            tree.processor_data.setdefault('heading_aliases', {})
            tree.processor_data.setdefault('heading_alias_nodes', set())
            tree.processor_data.setdefault('heading_link_nodes', set())

        @library.processor('heading-alias')
        def process_heading_alias(tree, node):
            init(tree)

            assert('name' in node.kwargs)

            for link in tree.processor_data['heading_link_nodes']:
                if link.kwargs['name'] == node.kwargs['name']:
                    tree.mark_node_dirty(link)

            document = find_ancestor(node, lambda n: n.name == 'Document')
            toc_node = None
            for maybe_h in preorder_traversal(document, node):
                if maybe_h.data.get('toc_entry', None):
                    toc_node = maybe_h
                    break

            if toc_node:
                tree.replace_node(node, CWEmptyNode())
                name = node.kwargs['name']
                toc_entry = toc_node.data['toc_entry']
                tree.processor_data['heading_aliases'][name] = toc_entry
            else:
                tree.processor_data['heading_alias_nodes'].add(node)

        @library.processor('h1')
        @library.processor('h2')
        @library.processor('h3')
        @library.processor('h4')
        @library.processor('h5')
        @library.processor('h6')
        def process_heading(tree, node):
            init(tree)
            for ha in tree.processor_data['heading_alias_nodes']:
                if ha.document_id == node.document_id:
                    tree.mark_node_dirty(ha)

        @library.processor('heading-link')
        def process_heading_link(tree, node):
            tree.processor_data.setdefault('heading_alias_nodes', set())
            assert('name' in node.kwargs)
            if node.kwargs['name'] in tree.processor_data['heading_aliases']:
                toc_entry =  tree.processor_data['heading_aliases'][node.kwargs['name']]
                link_node = CWLinkNode(toc_entry.ref_id)
                link_node.deepcopy_children_from(toc_entry.heading_node)
                tree.replace_subtree(node, link_node)
            else:
                tree.processor_data['heading_link_nodes'].add(node)


__all__ = ['HeadingAliasesPlugin']

def add_links(library):
    noop = lambda *args, **kwargs: None
    library.processor('Anchor', noop)
    library.processor('Link', noop)

    @library.processor('Anchor')
    def process_anchor(tree, node):
        tree.processor_data.setdefault('ref_id_to_anchor', {})
        ref_id_to_anchor = tree.processor_data['ref_id_to_anchor']
        if node.ref_id in ref_id_to_anchor:
            raise ValueError("Ref IDs must be globally unique")
        ref_id_to_anchor[node.ref_id] = node

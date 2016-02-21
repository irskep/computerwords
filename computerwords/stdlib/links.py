def add_links(library):
    noop = lambda *args, **kwargs: None
    library.processor('Anchor', noop)
    library.processor('Link', noop)

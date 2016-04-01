def add_basics(library):
    noop = lambda *args, **kwargs: None
    library.processor('Root', noop)
    library.processor('Empty', noop)
    library.processor('Text', noop)
    library.processor('Document', noop)

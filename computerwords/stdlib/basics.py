def add_basics(library):
    passthrough = lambda *args, **kwargs: None
    library.processor('Root', passthrough)
    library.processor('Text', passthrough)

def add_src_py(library):
    @library.processor('autodoc-module')
    def process_autodoc_module(tree, node):
        pass
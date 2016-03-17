class CWPlugin:
    CONFIG_NAMESPACE = None

    def get_default_config(self):
        return None

    def postprocess_config(self, config):
        pass

    def add_processors(self, library):
        pass

    WRITER_NAME = None
    def write(self, config, src_root, dest_root, stdlib, tree):
        pass

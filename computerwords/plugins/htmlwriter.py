import logging

from computerwords.htmlwriter import write as write_html
from computerwords.plugin import CWPlugin


log = logging.getLogger(__name__)


class HTMLWriterPlugin(CWPlugin):
    CONFIG_NAMESPACE = 'html'

    def get_default_config(self):
        return {
            "site_url": "/",
            "project_version": None,
            "css_files": None,
            "css_theme": "default",
            "static_dir_name": "static",
            "meta_description": "",
        }

    def postprocess_config(self, config):
        if not config['html']['site_url'].endswith('/'):
            config['html']['site_url'] += "/"

    def add_processors(self, library):
        pass

    WRITER_NAME = "html"
    def write(self, config, src_root, dest_root, stdlib, tree):
        write_html(config, src_root, dest_root, stdlib, tree)

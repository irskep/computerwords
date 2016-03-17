import argparse
import importlib
import json
import logging
import pathlib
import sys

logging.basicConfig(level=logging.DEBUG)

from computerwords.htmlwriter import write as write_html
from computerwords.config import DictCascade, DEFAULT_CONFIG
from computerwords.cwdom.nodes import CWRootNode
from computerwords.cwdom.CWTree import CWTree
from computerwords.plugin import CWPlugin
from computerwords.markdown_parser.cfm_to_cwdom import cfm_to_cwdom
from computerwords.read_doc_tree import read_doc_tree
from computerwords.stdlib import stdlib
from computerwords.stdlib.src_py import read_config

log = logging.getLogger(__name__)


def _get_plugins(plugin_names):
    for import_path in plugin_names:
        module = importlib.import_module(import_path)
        for attr in module.__all__:
            cls = getattr(module, attr)
            if issubclass(cls, CWPlugin):
                yield cls()


def run():
    p = argparse.ArgumentParser()
    p.add_argument('--conf', default="conf.json", type=argparse.FileType('r'))
    p.add_argument('--debug', default=False, action='store_true')
    args = p.parse_args()

    config_json = json.load(args.conf)
    plugin_names = DEFAULT_CONFIG['plugins'] + config_json.get('plugins', [])
    plugins = list(_get_plugins(plugin_names))
    more_defaults = [
        {plugin.CONFIG_NAMESPACE: plugin.get_default_config()}
        for plugin in plugins
        if plugin.CONFIG_NAMESPACE is not None
    ]

    config = dict(
        DictCascade(*([DEFAULT_CONFIG] + more_defaults + [config_json])))

    if not config['html']['site_url'].endswith('/'):
        config['html']['site_url'] += "/"

    files_root = pathlib.Path(args.conf.name).parent.resolve()
    config['root_dir'] = files_root
    output_root = pathlib.Path(files_root) / pathlib.Path(config['output_dir'])
    output_root.mkdir(exist_ok=True)

    read_config(config)

    for plugin in plugins:
        plugin.add_processors(stdlib)

    def _get_doc_cwdom(subtree):
        with subtree.root_path.open() as f:
            return cfm_to_cwdom(f.read(), stdlib.get_allowed_tags())

    doc_tree, document_nodes = read_doc_tree(
        files_root, config['file_hierarchy'], _get_doc_cwdom)
    tree = CWTree(CWRootNode(document_nodes), {
        'doc_tree': doc_tree,
        'output_dir': output_root,
        'config': config
    })
    if args.debug:
        print(tree.root.get_string_for_test_comparison())
    tree.apply_library(stdlib)


    write_html(config, files_root, output_root, stdlib, tree)

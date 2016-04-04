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
from computerwords.markdown_parser import CFMParserConfig
from computerwords.markdown_parser.cfm_to_cwdom import cfm_to_cwdom
from computerwords.read_doc_tree import read_doc_tree
from computerwords.stdlib import stdlib

log = logging.getLogger(__name__)


def _get_plugins(plugin_names):
    for import_path in plugin_names:
        module = importlib.import_module(import_path)
        for maybe_cls in module.__dict__.values():
            try:
                if issubclass(maybe_cls, CWPlugin):
                    yield maybe_cls()
            except TypeError:
                pass


def _get_cfm_reader(lib):
    def _read_doc_tree(toc_entry, doc_id, doc_path):
        config = CFMParserConfig(
            allowed_tags=lib.get_allowed_tags(),
            document_id=doc_id,
            document_path=doc_path)
        with toc_entry.root_path.open() as f:
            return cfm_to_cwdom(f.read(), config)
    return _read_doc_tree


def run():
    p = argparse.ArgumentParser()
    p.add_argument('--conf', default="conf.json", type=argparse.FileType('r'))
    p.add_argument('--debug', default=False, action='store_true')
    p.add_argument('--writer', default='html', action='store')
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

    files_root = pathlib.Path(args.conf.name).parent.resolve()
    config['root_dir'] = files_root
    output_root = pathlib.Path(files_root) / pathlib.Path(config['output_dir'])
    output_root.mkdir(exist_ok=True)

    for plugin in plugins:
        plugin.postprocess_config(config)

    for plugin in plugins:
        plugin.add_processors(stdlib)

    doc_tree, document_nodes = read_doc_tree(
        files_root, config['file_hierarchy'], _get_cfm_reader(stdlib))
    tree = CWTree(CWRootNode(document_nodes), {
        'doc_tree': doc_tree,
        'output_dir': output_root,
        'config': config
    })
    if args.debug:
        print(tree.root.get_string_for_test_comparison())
    tree.apply_library(stdlib)

    writers = {
        plugin.WRITER_NAME: plugin
        for plugin in plugins
        if plugin.WRITER_NAME is not None
    }
    writers[args.writer].write(config, files_root, output_root, stdlib, tree)

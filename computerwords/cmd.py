import argparse
import sys

from computerwords.kissup import string_to_cwdom
from computerwords.htmlwriter import cwdom_to_html_string
from computerwords.stdlib import stdlib


def run():
    p = argparse.ArgumentParser()
    p.add_argument('input_str')
    args = p.parse_args()

    node_store = string_to_cwdom(args.input_str, stdlib.get_allowed_tags())
    processed_node_store = stdlib.process_node_store(node_store)
    cwdom_to_html_string(stdlib, processed_node_store, sys.stdout)

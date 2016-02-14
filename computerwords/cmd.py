import argparse
import sys

from computerwords.kissup import string_to_cwdom
from computerwords.htmlwriter import cwdom_to_html_string
from computerwords.stdlib import stdlib


def run():
    p = argparse.ArgumentParser()
    p.add_argument('input_str')
    args = p.parse_args()

    input_str = args.input_str
    if input_str == '-':
        input_str = sys.stdin.read()

    node_store = string_to_cwdom(input_str, stdlib.get_allowed_tags())

    node_store.apply_library(stdlib)

    cwdom_to_html_string(stdlib, node_store, sys.stdout)

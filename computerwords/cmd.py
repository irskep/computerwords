import argparse
import sys

from computerwords.kissup import string_to_cwdom
from computerwords.htmlwriter import cwdom_to_html_string
from computerwords.processor import get_tag_names


def run():
    p = argparse.ArgumentParser()
    p.add_argument('input_str')
    args = p.parse_args()
    cwdom_to_html_string(string_to_cwdom(args.input_str, get_tag_names()), sys.stdout)

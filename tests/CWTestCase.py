import logging
import unittest
from textwrap import dedent

from computerwords.cwdom.CWDOMNode import CWDOMEndOfInputNode


log = logging.getLogger(__name__)


class CWTestCase(unittest.TestCase):
    END = CWDOMEndOfInputNode.NAME

    def strip(self, s):
        return dedent(s)[1:-1]

    def log_tree(self, ns):
        logging.basicConfig(level=logging.DEBUG)
        log.debug('\n' + ns.root.get_string_for_test_comparison())

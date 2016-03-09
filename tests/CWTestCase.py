import logging
import unittest
from textwrap import dedent


log = logging.getLogger(__name__)


class CWTestCase(unittest.TestCase):

    def setUp(self):
        self.maxDiff = None

    def strip(self, s):
        return dedent(s)[1:-1]

    def log_tree(self, tree):
        self.log_node(tree.root)

    def log_node(self, node):
        logging.basicConfig(level=logging.DEBUG)
        log.debug('\n' + node.get_string_for_test_comparison())

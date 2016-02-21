import logging
import unittest
from textwrap import dedent


log = logging.getLogger(__name__)


class CWTestCase(unittest.TestCase):
    def strip(self, s):
        return dedent(s)[1:-1]

    def log_tree(self, ns):
        logging.basicConfig(level=logging.DEBUG)
        log.debug('\n' + ns.root.get_string_for_test_comparison())
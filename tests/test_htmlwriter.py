from CWTestCase import CWTestCase


from computerwords.htmlwriter.util import find_path_between


class HTMLWriterUtilTestCase(CWTestCase):
    def test_find_self(self):
        self.assertEqual(
            find_path_between(('a',), ('a',)),
            "")

    def test_find_sibling(self):
        self.assertEqual(
            find_path_between(('a',), ('b',)),
            "b.html")

    def test_find_elsewhere(self):
        self.assertEqual(
            find_path_between(('a', 'b'), ('c', 'd')),
            "../c/d.html")
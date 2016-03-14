<!doctype html>
<html>
    <head>
        <title>computerwords/cwdom/nodes.py</title>
    </head>
    <body class="autodoc-source">

<a name=0><pre>"""
</pre></a>
        
<a name=1><pre>This module contains the nodes that make up the document tree.
</pre></a>
        
<a name=2><pre>
</pre></a>
        
<a name=3><pre>### Vocabulary
</pre></a>
        
<a name=4><pre>
</pre></a>
        
<a name=5><pre>* **Document ID, `document_id`, or `doc_id`**: a tuple of strings representing
</pre></a>
        
<a name=6><pre>  a document's relative path to the root of the source files. For example,
</pre></a>
        
<a name=7><pre>  `('api', 'index.md')`.
</pre></a>
        
<a name=8><pre>"""
</pre></a>
        
<a name=9><pre>
</pre></a>
        
<a name=10><pre>import logging
</pre></a>
        
<a name=11><pre>import weakref
</pre></a>
        
<a name=12><pre>
</pre></a>
        
<a name=13><pre>
</pre></a>
        
<a name=14><pre>log = logging.getLogger(__name__)
</pre></a>
        
<a name=15><pre>
</pre></a>
        
<a name=16><pre>
</pre></a>
        
<a name=17><pre>class _IDGenerator:
</pre></a>
        
<a name=18><pre>    def __init__(self):
</pre></a>
        
<a name=19><pre>        self.next_id = 1
</pre></a>
        
<a name=20><pre>
</pre></a>
        
<a name=21><pre>    def get_id(self):
</pre></a>
        
<a name=22><pre>        i = self.next_id
</pre></a>
        
<a name=23><pre>        self.next_id += 1
</pre></a>
        
<a name=24><pre>        return i
</pre></a>
        
<a name=25><pre>
</pre></a>
        
<a name=26><pre>
</pre></a>
        
<a name=27><pre>_id_generator = _IDGenerator()
</pre></a>
        
<a name=28><pre>
</pre></a>
        
<a name=29><pre>
</pre></a>
        
<a name=30><pre>class CWNode:
</pre></a>
        
<a name=31><pre>    """Superclass for all nodes. Unless you're writing test cases, you'll
</pre></a>
        
<a name=32><pre>    generally be dealing with subclasses of this."""
</pre></a>
        
<a name=33><pre>
</pre></a>
        
<a name=34><pre>    def __init__(self, name, children=None, document_id=None):
</pre></a>
        
<a name=35><pre>        """
</pre></a>
        
<a name=36><pre>        * `name`: aka type or kind of node
</pre></a>
        
<a name=37><pre>        * `children`: list of initial children
</pre></a>
        
<a name=38><pre>        * `document_id`: document ID of the document in which this node
</pre></a>
        
<a name=39><pre>          resides. Usually assigned after initialization by `CWTree`.
</pre></a>
        
<a name=40><pre>        """
</pre></a>
        
<a name=41><pre>        super().__init__()
</pre></a>
        
<a name=42><pre>
</pre></a>
        
<a name=43><pre>        self.document_id = document_id
</pre></a>
        
<a name=44><pre>
</pre></a>
        
<a name=45><pre>        if children is None:
</pre></a>
        
<a name=46><pre>            children = []
</pre></a>
        
<a name=47><pre>
</pre></a>
        
<a name=48><pre>        self.name = name
</pre></a>
        
<a name=49><pre>        self.children = children
</pre></a>
        
<a name=50><pre>        self.data = {}
</pre></a>
        
<a name=51><pre>
</pre></a>
        
<a name=52><pre>        self.parent_weakref = None
</pre></a>
        
<a name=53><pre>        self.claim_children()
</pre></a>
        
<a name=54><pre>
</pre></a>
        
<a name=55><pre>        self.id = name + ':' + str(_id_generator.get_id())
</pre></a>
        
<a name=56><pre>
</pre></a>
        
<a name=57><pre>    def claim_children(self):
</pre></a>
        
<a name=58><pre>        """Call `child.set_parent(self)` on each child"""
</pre></a>
        
<a name=59><pre>        for child in self.children:
</pre></a>
        
<a name=60><pre>            child.set_parent(self)
</pre></a>
        
<a name=61><pre>
</pre></a>
        
<a name=62><pre>    def set_children(self, children):
</pre></a>
        
<a name=63><pre>        """Replace `self.children` with a new list of children, and set their
</pre></a>
        
<a name=64><pre>        parent values"""
</pre></a>
        
<a name=65><pre>        assert(isinstance(children, list))
</pre></a>
        
<a name=66><pre>        self.children = children
</pre></a>
        
<a name=67><pre>        self.claim_children()
</pre></a>
        
<a name=68><pre>
</pre></a>
        
<a name=69><pre>    def get_parent(self):
</pre></a>
        
<a name=70><pre>        """Return this node's current parent, or `None` if there isn't one"""
</pre></a>
        
<a name=71><pre>        if self.parent_weakref is None:
</pre></a>
        
<a name=72><pre>            return None
</pre></a>
        
<a name=73><pre>        else:
</pre></a>
        
<a name=74><pre>            return self.parent_weakref()
</pre></a>
        
<a name=75><pre>
</pre></a>
        
<a name=76><pre>    def set_parent(self, new_parent):
</pre></a>
        
<a name=77><pre>        """Set this node's parent"""
</pre></a>
        
<a name=78><pre>        if new_parent is None:
</pre></a>
        
<a name=79><pre>            self.parent_weakref = None
</pre></a>
        
<a name=80><pre>        else:
</pre></a>
        
<a name=81><pre>            self.parent_weakref = weakref.ref(new_parent)
</pre></a>
        
<a name=82><pre>
</pre></a>
        
<a name=83><pre>    def deep_set_document_id(self, new_id):
</pre></a>
        
<a name=84><pre>        """Set the `document_id` of this node and all its children"""
</pre></a>
        
<a name=85><pre>        self.document_id = new_id
</pre></a>
        
<a name=86><pre>        for child in self.children:
</pre></a>
        
<a name=87><pre>            child.deep_set_document_id(new_id)
</pre></a>
        
<a name=88><pre>
</pre></a>
        
<a name=89><pre>    def copy(self):
</pre></a>
        
<a name=90><pre>        """Copy this node *but not its children*"""
</pre></a>
        
<a name=91><pre>        return CWNode(self.name, document_id=self.document_id)
</pre></a>
        
<a name=92><pre>
</pre></a>
        
<a name=93><pre>    def deepcopy(self):
</pre></a>
        
<a name=94><pre>        """Copy this node *and its children*"""
</pre></a>
        
<a name=95><pre>        node_copy = self.copy()
</pre></a>
        
<a name=96><pre>        node_copy.set_children([child.deepcopy() for child in self.children])
</pre></a>
        
<a name=97><pre>        return node_copy
</pre></a>
        
<a name=98><pre>
</pre></a>
        
<a name=99><pre>    def deepcopy_children_from(self, node, at_end=False):
</pre></a>
        
<a name=100><pre>        """Add a deep copy of all `node`'s descendants before or after existing
</pre></a>
        
<a name=101><pre>        children"""
</pre></a>
        
<a name=102><pre>        if at_end:
</pre></a>
        
<a name=103><pre>            self.set_children(self.children + [child.deepcopy() for child in node.children])
</pre></a>
        
<a name=104><pre>        else:
</pre></a>
        
<a name=105><pre>            self.set_children([child.deepcopy() for child in node.children] + self.children)
</pre></a>
        
<a name=106><pre>        return self
</pre></a>
        
<a name=107><pre>
</pre></a>
        
<a name=108><pre>    def get_string_for_test_comparison(self, inner_indentation=2):
</pre></a>
        
<a name=109><pre>        """Returns a string that is very convenient to compare using
</pre></a>
        
<a name=110><pre>        `unittest.TestCase.assertMultiLineEqual()`
</pre></a>
        
<a name=111><pre>        """
</pre></a>
        
<a name=112><pre>        elements = [
</pre></a>
        
<a name=113><pre>            "{}({})".format(
</pre></a>
        
<a name=114><pre>                self.name, self.get_args_string_for_test_comparison())
</pre></a>
        
<a name=115><pre>        ]
</pre></a>
        
<a name=116><pre>
</pre></a>
        
<a name=117><pre>        for child in self.children:
</pre></a>
        
<a name=118><pre>            inner_str = child.get_string_for_test_comparison(
</pre></a>
        
<a name=119><pre>                inner_indentation + 2)
</pre></a>
        
<a name=120><pre>            elements.append(' ' * inner_indentation + inner_str)
</pre></a>
        
<a name=121><pre>
</pre></a>
        
<a name=122><pre>        return '\n'.join(elements)
</pre></a>
        
<a name=123><pre>
</pre></a>
        
<a name=124><pre>    def get_args_string_for_test_comparison(self):
</pre></a>
        
<a name=125><pre>        """Subclasses may override this to populate arguments in test
</pre></a>
        
<a name=126><pre>        strings"""
</pre></a>
        
<a name=127><pre>        return ""
</pre></a>
        
<a name=128><pre>
</pre></a>
        
<a name=129><pre>    def __repr__(self):
</pre></a>
        
<a name=130><pre>        return '{}({!r})'.format(self.name, self.children)
</pre></a>
        
<a name=131><pre>
</pre></a>
        
<a name=132><pre>    def shallow_repr(self):
</pre></a>
        
<a name=133><pre>        """Like `self.__repr__()`, but don't include children"""
</pre></a>
        
<a name=134><pre>        return '{}()'.format(self.name)
</pre></a>
        
<a name=135><pre>
</pre></a>
        
<a name=136><pre>    def __eq__(self, other):
</pre></a>
        
<a name=137><pre>        return (type(self) is type(other) and self.id == other.id)
</pre></a>
        
<a name=138><pre>
</pre></a>
        
<a name=139><pre>    def __hash__(self):
</pre></a>
        
<a name=140><pre>        return hash(self.id)
</pre></a>
        
<a name=141><pre>
</pre></a>
        
<a name=142><pre>
</pre></a>
        
<a name=143><pre>class CWRootNode(CWNode):
</pre></a>
        
<a name=144><pre>    """The node at the root of a `CWTree`. Its immediate children should all
</pre></a>
        
<a name=145><pre>    be instances of `CWDocumentNode`."""
</pre></a>
        
<a name=146><pre>
</pre></a>
        
<a name=147><pre>    def __init__(self, children=None, document_id=None):
</pre></a>
        
<a name=148><pre>        super().__init__('Root', children, document_id=document_id)
</pre></a>
        
<a name=149><pre>
</pre></a>
        
<a name=150><pre>    def copy(self):
</pre></a>
        
<a name=151><pre>        return CWRootNode(document_id=self.document_id)
</pre></a>
        
<a name=152><pre>
</pre></a>
        
<a name=153><pre>    def shallow_repr(self):
</pre></a>
        
<a name=154><pre>        return '{}()'.format(self.name)
</pre></a>
        
<a name=155><pre>
</pre></a>
        
<a name=156><pre>
</pre></a>
        
<a name=157><pre>class CWDocumentNode(CWNode):
</pre></a>
        
<a name=158><pre>    """A node representing a document. Its descendants can be anything but
</pre></a>
        
<a name=159><pre>    `CWRootNode` and `CWDocumentNode`."""
</pre></a>
        
<a name=160><pre>
</pre></a>
        
<a name=161><pre>    def __init__(self, path, children=None, document_id=None):
</pre></a>
        
<a name=162><pre>        """
</pre></a>
        
<a name=163><pre>        * `path`: Filesystem path to this document
</pre></a>
        
<a name=164><pre>        """
</pre></a>
        
<a name=165><pre>        super().__init__('Document', children, document_id=document_id)
</pre></a>
        
<a name=166><pre>        self.path = path
</pre></a>
        
<a name=167><pre>
</pre></a>
        
<a name=168><pre>    def get_args_string_for_test_comparison(self):
</pre></a>
        
<a name=169><pre>        return 'path={!r}'.format(self.path)
</pre></a>
        
<a name=170><pre>
</pre></a>
        
<a name=171><pre>    def __repr__(self):
</pre></a>
        
<a name=172><pre>        return '{}(path={!r}, children={!r})'.format(
</pre></a>
        
<a name=173><pre>            self.name, self.path, self.children)
</pre></a>
        
<a name=174><pre>
</pre></a>
        
<a name=175><pre>    def shallow_repr(self):
</pre></a>
        
<a name=176><pre>        return '{}(path={!r})'.format(self.name, self.path)
</pre></a>
        
<a name=177><pre>
</pre></a>
        
<a name=178><pre>    def copy(self):
</pre></a>
        
<a name=179><pre>        return CWDocumentNode(self.path, document_id=document_id)
</pre></a>
        
<a name=180><pre>
</pre></a>
        
<a name=181><pre>
</pre></a>
        
<a name=182><pre>class CWTagNode(CWNode):
</pre></a>
        
<a name=183><pre>    """A node that can be directly converted to valid HTML."""
</pre></a>
        
<a name=184><pre>
</pre></a>
        
<a name=185><pre>    def __init__(self, name, kwargs, children=None, document_id=None):
</pre></a>
        
<a name=186><pre>        """
</pre></a>
        
<a name=187><pre>        * `name`: Still the type/kind of node, but is also a valid HTML tag
</pre></a>
        
<a name=188><pre>          name.
</pre></a>
        
<a name=189><pre>        * `kwargs`: Arguments/attributes parsed from the tag or inserted by
</pre></a>
        
<a name=190><pre>          processors.
</pre></a>
        
<a name=191><pre>        """
</pre></a>
        
<a name=192><pre>        super().__init__(name, children, document_id=document_id)
</pre></a>
        
<a name=193><pre>        assert isinstance(kwargs, dict)
</pre></a>
        
<a name=194><pre>        self.kwargs = kwargs
</pre></a>
        
<a name=195><pre>
</pre></a>
        
<a name=196><pre>    def copy(self, name=None, kwargs=None):
</pre></a>
        
<a name=197><pre>        return CWTagNode(
</pre></a>
        
<a name=198><pre>            name=name or self.name,
</pre></a>
        
<a name=199><pre>            kwargs=kwargs or self.kwargs,
</pre></a>
        
<a name=200><pre>            document_id=self.document_id)
</pre></a>
        
<a name=201><pre>
</pre></a>
        
<a name=202><pre>    def get_args_string_for_test_comparison(self):
</pre></a>
        
<a name=203><pre>        return 'kwargs={!r}'.format(self.kwargs)
</pre></a>
        
<a name=204><pre>
</pre></a>
        
<a name=205><pre>    def __repr__(self):
</pre></a>
        
<a name=206><pre>        return '{}(kwargs={!r}, children={!r})'.format(
</pre></a>
        
<a name=207><pre>            self.name, self.kwargs, self.children)
</pre></a>
        
<a name=208><pre>
</pre></a>
        
<a name=209><pre>    def shallow_repr(self):
</pre></a>
        
<a name=210><pre>        return '{}(kwargs={!r})'.format(self.name, self.kwargs)
</pre></a>
        
<a name=211><pre>
</pre></a>
        
<a name=212><pre>    def __eq__(self, other):
</pre></a>
        
<a name=213><pre>        return super().__eq__(other) and self.kwargs == other.kwargs
</pre></a>
        
<a name=214><pre>
</pre></a>
        
<a name=215><pre>    def __hash__(self):
</pre></a>
        
<a name=216><pre>        return hash(self.id)
</pre></a>
        
<a name=217><pre>
</pre></a>
        
<a name=218><pre>    def get_arg(self, name):
</pre></a>
        
<a name=219><pre>        return self.kwargs[name]
</pre></a>
        
<a name=220><pre>
</pre></a>
        
<a name=221><pre>
</pre></a>
        
<a name=222><pre>class CWTextNode(CWNode):
</pre></a>
        
<a name=223><pre>    """A node that only contains text to be written to output."""
</pre></a>
        
<a name=224><pre>
</pre></a>
        
<a name=225><pre>    def __init__(self, text, document_id=None, escape=True):
</pre></a>
        
<a name=226><pre>        """
</pre></a>
        
<a name=227><pre>        * `text`: The text
</pre></a>
        
<a name=228><pre>        * `escape`: If `True`, output should be escaped in whatever the output
</pre></a>
        
<a name=229><pre>          language is. Defaults to `True`.
</pre></a>
        
<a name=230><pre>        """
</pre></a>
        
<a name=231><pre>
</pre></a>
        
<a name=232><pre>        super().__init__('Text', [], document_id=document_id)
</pre></a>
        
<a name=233><pre>        self.escape = escape
</pre></a>
        
<a name=234><pre>        self.text = text
</pre></a>
        
<a name=235><pre>
</pre></a>
        
<a name=236><pre>    def get_string_for_test_comparison(self, inner_indentation=2):
</pre></a>
        
<a name=237><pre>        return repr(self.text)
</pre></a>
        
<a name=238><pre>
</pre></a>
        
<a name=239><pre>    def copy(self):
</pre></a>
        
<a name=240><pre>        return CWTextNode(self.text)
</pre></a>
        
<a name=241><pre>
</pre></a>
        
<a name=242><pre>    def get_args_string_for_test_comparison(self):
</pre></a>
        
<a name=243><pre>        return repr(self.text)
</pre></a>
        
<a name=244><pre>
</pre></a>
        
<a name=245><pre>    def __repr__(self):
</pre></a>
        
<a name=246><pre>        return "{}(text={!r})".format(self.name, self.text)
</pre></a>
        
<a name=247><pre>
</pre></a>
        
<a name=248><pre>
</pre></a>
        
<a name=249><pre>class CWAnchorNode(CWTagNode):
</pre></a>
        
<a name=250><pre>    """
</pre></a>
        
<a name=251><pre>    A node that can be linked to via its globally unique `ref_id`. Essentially
</pre></a>
        
<a name=252><pre>    a specialized version of `CWTagNode('a', {'name': ...})`.
</pre></a>
        
<a name=253><pre>    """
</pre></a>
        
<a name=254><pre>
</pre></a>
        
<a name=255><pre>    def __init__(self, ref_id, kwargs=None, children=None, document_id=None):
</pre></a>
        
<a name=256><pre>        """
</pre></a>
        
<a name=257><pre>        * `ref_id`: Globally unique ID of this anchor
</pre></a>
        
<a name=258><pre>        """
</pre></a>
        
<a name=259><pre>        super().__init__(
</pre></a>
        
<a name=260><pre>            'Anchor', kwargs or {}, children, document_id=document_id)
</pre></a>
        
<a name=261><pre>        self.ref_id = ref_id
</pre></a>
        
<a name=262><pre>
</pre></a>
        
<a name=263><pre>    def get_args_string_for_test_comparison(self):
</pre></a>
        
<a name=264><pre>        return "ref_id={!r}, kwargs={!r}".format(self.ref_id, self.kwargs)
</pre></a>
        
<a name=265><pre>
</pre></a>
        
<a name=266><pre>    def copy(self):
</pre></a>
        
<a name=267><pre>        return CWAnchorNode(
</pre></a>
        
<a name=268><pre>            self.ref_id, self.kwargs, document_id=document_id)
</pre></a>
        
<a name=269><pre>
</pre></a>
        
<a name=270><pre>    def __repr__(self):
</pre></a>
        
<a name=271><pre>        return "{}(ref_id={!r}, kwargs={!r}, children={!r})".format(
</pre></a>
        
<a name=272><pre>            self.name, self.ref_id, self.kwargs, self.children)
</pre></a>
        
<a name=273><pre>
</pre></a>
        
<a name=274><pre>    def shallow_repr(self):
</pre></a>
        
<a name=275><pre>        return "{}(ref_id={!r}, kwargs={!r})".format(
</pre></a>
        
<a name=276><pre>            self.name, self.ref_id, self.kwargs)
</pre></a>
        
<a name=277><pre>
</pre></a>
        
<a name=278><pre>
</pre></a>
        
<a name=279><pre>class CWLinkNode(CWNode):
</pre></a>
        
<a name=280><pre>    """
</pre></a>
        
<a name=281><pre>    A node that can link to the location of a `CWAnchorNode` to via its
</pre></a>
        
<a name=282><pre>    globally unique `ref_id`.
</pre></a>
        
<a name=283><pre>
</pre></a>
        
<a name=284><pre>    In the future, this may become a subclass of `CWTagNode`.
</pre></a>
        
<a name=285><pre>    """
</pre></a>
        
<a name=286><pre>
</pre></a>
        
<a name=287><pre>    def __init__(self, ref_id, children=None, document_id=None):
</pre></a>
        
<a name=288><pre>        super().__init__('Link', children, document_id=document_id)
</pre></a>
        
<a name=289><pre>        self.ref_id = ref_id
</pre></a>
        
<a name=290><pre>
</pre></a>
        
<a name=291><pre>    def get_args_string_for_test_comparison(self):
</pre></a>
        
<a name=292><pre>        return "ref_id={!r}".format(self.ref_id)
</pre></a>
        
<a name=293><pre>
</pre></a>
        
<a name=294><pre>    def copy(self):
</pre></a>
        
<a name=295><pre>        return CWLinkNode(self.ref_id, document_id=self.document_id)
</pre></a>
        
<a name=296><pre>
</pre></a>
        
<a name=297><pre>    def __repr__(self):
</pre></a>
        
<a name=298><pre>        return "{}(ref_id={!r}, children={!r})".format(
</pre></a>
        
<a name=299><pre>            self.name, self.ref_id, self.children)
</pre></a>
        
<a name=300><pre>
</pre></a>
        
<a name=301><pre>    def shallow_repr(self):
</pre></a>
        
<a name=302><pre>        return "{}(ref_id={!r})".format(self.name, self.ref_id)
</pre></a>
        
<a name=303><pre>
</pre></a>
        
<a name=304><pre>
</pre></a>
        
<a name=305><pre>class CWDocumentLinkNode(CWNode):
</pre></a>
        
<a name=306><pre>    """
</pre></a>
        
<a name=307><pre>    A node that can link to the location of a document without including any
</pre></a>
        
<a name=308><pre>    anchors inside the page.
</pre></a>
        
<a name=309><pre>    """
</pre></a>
        
<a name=310><pre>
</pre></a>
        
<a name=311><pre>    def __init__(self, target_document_id, children=None, document_id=None):
</pre></a>
        
<a name=312><pre>        super().__init__('DocumentLink', children, document_id=document_id)
</pre></a>
        
<a name=313><pre>        self.target_document_id = target_document_id
</pre></a>
        
<a name=314><pre>
</pre></a>
        
<a name=315><pre>    def get_args_string_for_test_comparison(self):
</pre></a>
        
<a name=316><pre>        return "target_document_id={!r}".format(self.target_document_id)
</pre></a>
        
<a name=317><pre>
</pre></a>
        
<a name=318><pre>    def copy(self):
</pre></a>
        
<a name=319><pre>        return CWDocumentLinkNode(
</pre></a>
        
<a name=320><pre>            self.target_document_id, document_id=self.document_id)
</pre></a>
        
<a name=321><pre>
</pre></a>
        
<a name=322><pre>    def __repr__(self):
</pre></a>
        
<a name=323><pre>        return "{}(target_document_id={!r}, children={!r})".format(
</pre></a>
        
<a name=324><pre>            self.name, self.target_document_id, self.children)
</pre></a>
        
<a name=325><pre>
</pre></a>
        
<a name=326><pre>    def shallow_repr(self):
</pre></a>
        
<a name=327><pre>        return "{}(target_document_id={!r})".format(
</pre></a>
        
<a name=328><pre>            self.name, self.target_document_id)
</pre></a>
        
    </body>
</html>
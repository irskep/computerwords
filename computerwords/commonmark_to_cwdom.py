import re

from collections import OrderedDict

import CommonMark

from computerwords.cwdom.CWDOMNode import *
from computerwords.kissup.lexer import lex_kissup
from computerwords.kissup.parser import (
    parse_open_tag,
    parse_close_tag,
    parse_self_closing_tag,
)


class UnparsedTagNode(CWDOMNode):
    def __init__(self, literal):
        super().__init__('UnparsedTag')
        self.literal = literal


def _dump(ast_node):
    for k, v in sorted(vars(ast_node).items()):
        if isinstance(v, dict):
            v = OrderedDict(sorted(v.items()))
        print("{}: {!r}".format(k, v))


AST_TYPE_TO_CWDOM = {}
def t(name):
    def dec(f):
        AST_TYPE_TO_CWDOM[name] = f
        return f
    return dec


AST_TYPE_TO_CWDOM_POST = {}
def post(name):
    def dec(f):
        AST_TYPE_TO_CWDOM_POST[name] = f
        return f
    return dec


@t('Document')
def t_Document(ast_node):
    return CWDOMDocumentNode('PATH')

@t('Heading')
def t_Header(ast_node):
    return CWDOMTagNode('h{}'.format(ast_node.level), {})

@t('Text')
def t_Text(ast_node):
    return CWDOMTextNode(ast_node.literal)

@t('Paragraph')
def t_Paragraph(ast_node):
    return CWDOMTagNode('p', {})

@t('Link')
def t_Link(ast_node):
    return CWDOMTagNode('a', {'href': ast_node.destination})

@t('List')
def t_List(ast_node):
    if ast_node.list_data['type'] == 'Bullet':
        return CWDOMTagNode('ul', {})
    elif ast_node.list_data['type'] == 'Ordered': 
        return CWDOMTagNode('ol', {})
    else:
        raise ValueError("Unknown list type: {}".format(
            ast_node.list_data['type']))

@t('Item')
def t_Item(ast_node):
    return CWDOMTagNode('li', {})

@t('HtmlBlock')
def t_HtmlBlock(ast_node):
    return CWDOMTagNode('pre', {}, [CWDOMTextNode(ast_node.literal)])

@t('HtmlInline')
def t_HtmlInline(ast_node):
    return CWDOMTagNode('tt', {}, [CWDOMTextNode(ast_node.literal)])

@t('Emph')
def t_Emph(ast_node):
    return CWDOMTagNode('i', {})

@t('Strong')
def t_Strong(ast_node):
    return CWDOMTagNode('strong', {})

@t('BlockQuote')
def t_BlockQuote(ast_node):
    return CWDOMTagNode('blockquote', {})

@t('ThematicBreak')
def t_ThematicBreak(ast_node):
    return CWDOMTagNode('hr', {})

@t('CodeBlock')
def t_CodeBlock(ast_node):
    return CWDOMTagNode('pre', {'language': ast_node.info})

@t('Code')
def t_Code(ast_node):
    return CWDOMTagNode('tt', {}, [CWDOMTextNode(ast_node.literal)])

@t('Hardbreak')
def t_Hardbreak(ast_node):
    return CWDOMTagNode('br', {})

@t('Softbreak')
def t_Softbreak(ast_node):
    # optionally insert br here
    return CWDOMTextNode('')

@t('Image')
def t_Image(ast_node):
    return CWDOMTagNode('img', {'src': ast_node.destination})

@post('Image')
def post_Image(node):
    node.kwargs['alt'] = node.children[0].text
    node.set_children([])


def _ast_node_to_cwdom(ast_node):
    cwdom_node = AST_TYPE_TO_CWDOM[ast_node.t](ast_node)
    children = []
    ast_child = ast_node.first_child
    while ast_child:
        children.append(_ast_node_to_cwdom(ast_child))
        ast_child = ast_child.nxt
    # node might have added its own children (see Code)
    cwdom_node.set_children(cwdom_node.children + children)
    if ast_node.t in AST_TYPE_TO_CWDOM_POST:
        AST_TYPE_TO_CWDOM_POST[ast_node.t](cwdom_node)
    return cwdom_node


def fix_ignored_html(node):
    children = node.children
    left_i = None
    for i, child in enumerate(children):
        if isinstance(child, UnparsedTagNode):
            left_i = i
            break

    if left_i is None:
        for child in node.children:
            fix_ignored_html(child)
        return

    print("----------")
    left_node = parse_open_tag(lex_kissup(node.literal))
    print(left_node)


def commonmark_to_cwdom(text):
    parser = CommonMark.blocks.Parser()
    doc_node = _ast_node_to_cwdom(parser.parse(text))
    fix_ignored_html(doc_node)
    return doc_node.children

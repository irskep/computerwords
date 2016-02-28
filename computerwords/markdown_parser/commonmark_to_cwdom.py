import re

from collections import OrderedDict

import CommonMark

from computerwords.cwdom.CWDOMNode import *
from .html_lexer import lex_html
from .html_parser import (
    parse_open_tag,
    parse_close_tag,
    parse_self_closing_tag,
)

### begin __init__.py ###

from .html_parser import parse_html

def lex_and_parse_html(string, allowed_tags):
    return parse_html(list(lex_html(string)), allowed_tags=allowed_tags)


def string_to_cwdom(string, config):
    return parse_tree_to_cwdom(lex_and_parse_html(string, config), config)

### end __init__.py ###

### begin parse_tree_to_cwdom ###

from .ast import StmtsNode, TagArgsNode
from .html_parser import ParseError
from computerwords.cwdom.CWDOMNode import *
from computerwords.cwdom.NodeStore import NodeStore
from .parse_tree_to_cwdom_util import *


def parse_tree_to_cwdom(root, config):
    return list(stmts_to_list(root, config))


def stmts_to_list(stmts, config):
    assert type(stmts) is StmtsNode
    if stmts.form_num == 1:
        yield from (
            list(stmt_to_tag_or_text(stmts.stmt, config)) +
            list(stmts_to_list(stmts.stmts, config))
        )


def stmt_to_tag_or_text(stmt, config):
    if stmt.form_num == 1:
        #yield CWDOMTextNode(stmt.text.value)
        yield from commonmark_to_cwdom(stmt.text.value, config)
    else:
        tag_node = stmt.tag
        if tag_node.form_num == 1:
            tag_contents = tag_node.open_tag.tag_contents
            yield CWDOMTagNode(
                tag_contents.bbword.value,
                tag_contents_to_kwargs(tag_contents),
                list(stmts_to_list(tag_node.stmts, config)))
        else:
            tag_contents = tag_node.self_closing_tag.tag_contents
            yield CWDOMTagNode(
                tag_contents.bbword.value,
                tag_contents_to_kwargs(tag_contents))

### end parse_tree_to_cwdom ###


class UnparsedTagNode(CWDOMNode):
    def __init__(self, literal):
        super().__init__('UnparsedTag')
        self.literal = literal

    def get_args_string_for_test_comparison(self):
        return repr(self.literal)

    def __repr__(self):
        return "{}(literal={!r})".format(self.name, self.literal)


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


@t('Text')
def t_Text(ast_node, config):
    yield CWDOMTextNode(ast_node.literal)

@t('Document')
def t_Document(ast_node, config):
    yield CWDOMDocumentNode('PATH')

@t('Heading')
def t_Header(ast_node, config):
    yield CWDOMTagNode('h{}'.format(ast_node.level), {})

@t('Paragraph')
def t_Paragraph(ast_node, config):
    yield CWDOMTagNode('p', {})

@t('Link')
def t_Link(ast_node, config):
    yield CWDOMTagNode('a', {'href': ast_node.destination})

@t('List')
def t_List(ast_node, config):
    if ast_node.list_data['type'] == 'Bullet':
        yield CWDOMTagNode('ul', {})
    elif ast_node.list_data['type'] == 'Ordered': 
        yield CWDOMTagNode('ol', {})
    else:
        raise ValueError("Unknown list type: {}".format(
            ast_node.list_data['type']))

@t('Item')
def t_Item(ast_node, config):
    yield CWDOMTagNode('li', {})

@t('HtmlBlock')
def t_HtmlBlock(ast_node, config):
    self_closing_tag = maybe_parse_self_closing_tag(ast_node.literal)
    if self_closing_tag:  # infinite loop if we don't short circuit(?)
        yield self_closing_tag
    else:
        yield from string_to_cwdom(ast_node.literal, config)

@t('HtmlInline')
def t_HtmlInline(ast_node, config):
    yield UnparsedTagNode(ast_node.literal)

@t('Emph')
def t_Emph(ast_node, config):
    yield CWDOMTagNode('i', {})

@t('Strong')
def t_Strong(ast_node, config):
    yield CWDOMTagNode('strong', {})

@t('BlockQuote')
def t_BlockQuote(ast_node, config):
    yield CWDOMTagNode('blockquote', {})

@t('ThematicBreak')
def t_ThematicBreak(ast_node, config):
    yield CWDOMTagNode('hr', {})

@t('CodeBlock')
def t_CodeBlock(ast_node, config):
    yield CWDOMTagNode(
        'pre', {'language': ast_node.info}, [CWDOMTextNode(ast_node.literal)])

@t('Code')
def t_Code(ast_node, config):
    yield CWDOMTagNode('tt', {}, [CWDOMTextNode(ast_node.literal)])

@t('Hardbreak')
def t_Hardbreak(ast_node, config):
    yield CWDOMTagNode('br', {})

@t('Softbreak')
def t_Softbreak(ast_node, config):
    # optionally insert br here
    yield CWDOMTextNode('')

@t('Image')
def t_Image(ast_node, config):
    yield CWDOMTagNode('img', {'src': ast_node.destination})

@post('Image')
def post_Image(node, config):
    node.kwargs['alt'] = node.children[0].text
    node.set_children([])


def maybe_parse_self_closing_tag(literal):
    tokens = list(lex_html(literal))
    ast = parse_self_closing_tag(tokens)
    if ast:
        return CWDOMTagNode(
            ast.tag_contents.bbword.value,
            tag_contents_to_kwargs(ast.tag_contents))
    else:
        return None


def fix_ignored_html(node):
    children = node.children
    left_i = None
    new_tag = None

    # replace self-closing tags
    for i, child in enumerate(children):
        if isinstance(child, UnparsedTagNode):
            self_closing_tag = maybe_parse_self_closing_tag(child.literal)
            if self_closing_tag:
                node.children[i] = self_closing_tag

    for i, child in enumerate(children):
        if isinstance(child, UnparsedTagNode):
            tokens = list(lex_html(child.literal))
            ast = parse_open_tag(tokens)
            if ast:
                left_i = i
                new_tag = CWDOMTagNode(
                    ast.tag_contents.bbword.value,
                    tag_contents_to_kwargs(ast.tag_contents))
                break

    if new_tag is None:
        for child in node.children:
            fix_ignored_html(child)
        return

    right_i = None
    for i, child in reversed(list(enumerate(children))):
        if i <= left_i:
            raise ValueError("Matching tag not found for {}".format(
                new_tag.name))
        if isinstance(child, UnparsedTagNode):
            tokens = list(lex_html(child.literal))
            ast = parse_close_tag(tokens)
            if ast:
                tag_name = ast.bbword.value
                if tag_name != new_tag.name:
                    raise ValueError("Mismatched closing tag: {} vs {}".format(
                        new_tag.name, tag_name))
                right_i = i
                break

    sub_children = children[left_i+1:right_i]
    del node.children[left_i+1:right_i+1]
    node.children[left_i] = new_tag
    new_tag.set_children(sub_children)
    node.claim_children()

    for child in node.children:
        fix_ignored_html(child)


def _ast_node_to_cwdom(ast_node, config):
    for cwdom_node in AST_TYPE_TO_CWDOM[ast_node.t](ast_node, config):
        children = []
        ast_child = ast_node.first_child
        while ast_child:
            for child in _ast_node_to_cwdom(ast_child, config):
                children.append(child)
            ast_child = ast_child.nxt
        # node might have added its own children (see Code)
        cwdom_node.set_children(cwdom_node.children + children)
        if ast_node.t in AST_TYPE_TO_CWDOM_POST:
            AST_TYPE_TO_CWDOM_POST[ast_node.t](cwdom_node)
        yield cwdom_node


def _replace_lone_p(nodes):
    if len(nodes) == 1 and nodes[0].name == 'p':
        return nodes[0].children
    else:
        return nodes


def commonmark_to_cwdom(text, config):
    parser = CommonMark.blocks.Parser()
    doc_node = list(_ast_node_to_cwdom(parser.parse(text), config))[0]
    fix_ignored_html(doc_node)
    return _replace_lone_p(doc_node.children)

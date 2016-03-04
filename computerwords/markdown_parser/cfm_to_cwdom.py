import re

from collections import OrderedDict

import CommonMark

from computerwords.cwdom.nodes import *
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


def html_string_to_cwdom(string, config):
    return parse_tree_to_cwdom(lex_and_parse_html(string, config), config)

### end __init__.py ###

### begin parse_tree_to_cwdom ###

from .ast import StmtsNode, TagArgsNode
from .html_parser import ParseError
from computerwords.cwdom.nodes import *
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
        yield from commonmark_to_cwdom(stmt.text.value, config)
    else:
        tag_node = stmt.tag
        if tag_node.form_num == 1:
            tag_contents = tag_node.open_tag.tag_contents
            yield CWTagNode(
                tag_contents.bbword.value,
                tag_contents_to_kwargs(tag_contents),
                list(stmts_to_list(tag_node.stmts, config)))
        else:
            tag_contents = tag_node.self_closing_tag.tag_contents
            yield CWTagNode(
                tag_contents.bbword.value,
                tag_contents_to_kwargs(tag_contents))

### end parse_tree_to_cwdom ###


class UnparsedTagNode(CWNode):
    def __init__(self, name, parse_tree, literal):
        super().__init__(name)
        self.parse_tree = parse_tree
        self.literal = literal

    def get_args_string_for_test_comparison(self):
        return repr(self.literal)

    def __repr__(self):
        return "{}(parse_tree={!r})".format(self.name, self.parse_tree)


class UnparsedOpenTagNode(UnparsedTagNode):
    def __init__(self, parse_tree, literal):
        super().__init__('UnparsedOpenTag', parse_tree, literal)


class UnparsedCloseTagNode(UnparsedTagNode):
    def __init__(self, parse_tree, literal):
        super().__init__('UnparsedCloseTag', parse_tree, literal)


def _dump(ast_node):
    for k, v in sorted(vars(ast_node).items()):
        if isinstance(v, dict):
            v = OrderedDict(sorted(v.items()))
        print("{}: {!r}".format(k, v))


AST_TYPE_TO_CW = {}
def t(name):
    def dec(f):
        AST_TYPE_TO_CW[name] = f
        return f
    return dec


AST_TYPE_TO_CW_POST = {}
def post(name):
    def dec(f):
        AST_TYPE_TO_CW_POST[name] = f
        return f
    return dec


@t('Text')
def t_Text(ast_node, config):
    yield CWTextNode(ast_node.literal)

@t('Document')
def t_Document(ast_node, config):
    yield CWDocumentNode('PATH')

@t('Heading')
def t_Header(ast_node, config):
    yield CWTagNode('h{}'.format(ast_node.level), {})

@t('Paragraph')
def t_Paragraph(ast_node, config):
    yield CWTagNode('p', {})

@t('Link')
def t_Link(ast_node, config):
    yield CWTagNode('a', {'href': ast_node.destination})

@t('List')
def t_List(ast_node, config):
    if ast_node.list_data['type'] == 'Bullet':
        yield CWTagNode('ul', {})
    elif ast_node.list_data['type'] == 'Ordered': 
        yield CWTagNode('ol', {})
    else:
        raise ValueError("Unknown list type: {}".format(
            ast_node.list_data['type']))

@t('Item')
def t_Item(ast_node, config):
    yield CWTagNode('li', {})

@t('HtmlBlock')
def t_HtmlBlock(ast_node, config):
    try:
        items = list(html_string_to_cwdom(ast_node.literal, config))
        yield from items
    except ParseError:
        yield from _do_your_best(ast_node.literal)

@t('HtmlInline')
def t_HtmlInline(ast_node, config):
    yield from _do_your_best(ast_node.literal)

@t('Emph')
def t_Emph(ast_node, config):
    yield CWTagNode('i', {})

@t('Strong')
def t_Strong(ast_node, config):
    yield CWTagNode('strong', {})

@t('BlockQuote')
def t_BlockQuote(ast_node, config):
    yield CWTagNode('blockquote', {})

@t('ThematicBreak')
def t_ThematicBreak(ast_node, config):
    yield CWTagNode('hr', {})

@t('CodeBlock')
def t_CodeBlock(ast_node, config):
    yield CWTagNode(
        'pre', {'language': ast_node.info}, [CWTextNode(ast_node.literal)])

@t('Code')
def t_Code(ast_node, config):
    yield CWTagNode('tt', {}, [CWTextNode(ast_node.literal)])

@t('Hardbreak')
def t_Hardbreak(ast_node, config):
    yield CWTagNode('br', {})

@t('Softbreak')
def t_Softbreak(ast_node, config):
    # optionally insert br here
    yield CWTextNode(' ')

@t('Image')
def t_Image(ast_node, config):
    yield CWTagNode('img', {'src': ast_node.destination})

@post('Image')
def post_Image(node, config):
    node.kwargs['alt'] = node.children[0].text
    node.set_children([])


class NonFatalParseError(Exception): pass


def _do_your_best(literal):
    try:
        yield from maybe_parse_self_closing_tag(literal)
        return
    except NonFatalParseError:
        pass

    try:
        yield from maybe_parse_open_tag(literal)
        return
    except NonFatalParseError:
        pass


    try:
        yield from maybe_parse_close_tag(literal)
        return
    except NonFatalParseError:
        pass

    raise ValueError("HTML parser can't handle {!r}".format(literal))


def _yield_nodes(literal, tokens, i, node):
    yield node
    if i < len(tokens) - 1:
        yield CWTextNode(literal[tokens[i].pos:])


def maybe_parse_self_closing_tag(literal):
    tokens = list(lex_html(literal))
    result = parse_self_closing_tag(tokens)
    if result:
        yield from _yield_nodes(literal, tokens, result[1], CWTagNode(
            result[0].tag_contents.bbword.value,
            tag_contents_to_kwargs(result[0].tag_contents)))
    else:
        raise NonFatalParseError()


def maybe_parse_open_tag(literal):
    tokens = list(lex_html(literal))
    result = parse_open_tag(tokens)
    if result:
        yield from _yield_nodes(
            literal, tokens, result[1], UnparsedOpenTagNode(result[0], literal))
    else:
        raise NonFatalParseError()


def maybe_parse_close_tag(literal):
    tokens = list(lex_html(literal))
    result = parse_close_tag(tokens)
    if result:
        yield from _yield_nodes(
            literal, tokens, result[1], UnparsedCloseTagNode(result[0], literal))
    else:
        raise NonFatalParseError()


class NoMatchingTagError(Exception): pass


def fix_ignored_html(node):
    children = node.children
    left_i = None
    new_tag = None

    for i, child in enumerate(children):
        if isinstance(child, UnparsedOpenTagNode):
            new_tag = CWTagNode(
                child.parse_tree.tag_contents.bbword.value,
                tag_contents_to_kwargs(child.parse_tree.tag_contents))
            left_i = i
            break

    if new_tag is not None:
        right_i = None
        for i, child in reversed(list(enumerate(children))):
            if i <= left_i:
                raise NoMatchingTagError("Matching tag not found for {}".format(
                    new_tag.name))
            if isinstance(child, UnparsedCloseTagNode):
                tag_name = child.parse_tree.bbword.value
                if tag_name != new_tag.name:
                    raise NoMatchingTagError("Mismatched closing tag: {} vs {}".format(
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
    #i = 0
    #while i < len(node.children):
    #    try:
    #        fix_ignored_html(node.children[i])
    #        i += 1
    #    except NoMatchingTagError as e:
    #        # this may have been caused by a tag being split across multiple
    #        # paragraphs. Fix by just concatenating paragraphs together until
    #        # it works.
    #        # TODO: then serialize and re-parse
    #        if i + 1 < len(node.children):
    #            node.children[i + 1].children = node.children[i].children + node.children[i + 1].children
    #            node.children.pop(i)
    #            node.children[i].claim_children()
    #        else:
    #            raise e


def _ast_node_to_cwdom(ast_node, config):
    for cwdom_node in AST_TYPE_TO_CW[ast_node.t](ast_node, config):
        children = []
        ast_child = ast_node.first_child
        while ast_child:
            for child in _ast_node_to_cwdom(ast_child, config):
                children.append(child)
            ast_child = ast_child.nxt
        # node might have added its own children (see Code)
        cwdom_node.set_children(cwdom_node.children + children)
        if ast_node.t in AST_TYPE_TO_CW_POST:
            AST_TYPE_TO_CW_POST[ast_node.t](cwdom_node)
        yield cwdom_node


def _replace_lone_p(nodes):
    if len(nodes) == 1 and nodes[0].name == 'p':
        return nodes[0].children
    else:
        return nodes


def commonmark_to_cwdom(text, config, fix_tags=True):
    parser = CommonMark.blocks.Parser()
    doc_node = list(_ast_node_to_cwdom(parser.parse(text), config))[0]
    if fix_tags:
        fix_ignored_html(doc_node)
    return _replace_lone_p(doc_node.children)


def cfm_to_cwdom(text, config, fix_tags=True):
    return commonmark_to_cwdom(text, config, fix_tags)

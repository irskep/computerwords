# useful reference: http://greentreesnakes.readthedocs.org/en/latest/nodes.html

import argparse
import ast
import json
import logging
import pathlib
import sys


logging.basicConfig()
log = logging.getLogger(__name__)


next_id = 0
def get_next_id():
    global next_id
    next_id += 1
    return next_id


MODULE_NAME_TO_ID = {}


def get_line(
        id, type, name, docstring, parent_id, string_inside_parens=None,
        return_value=None, line_number=None, source_file_path=None,
        relative_path=None):
    return {
        'id': id,
        'type': type,
        'name': name,
        'docstring': docstring,
        'parent_id': parent_id,
        'string_inside_parens': string_inside_parens,
        'return_value': return_value,
        'line_number': line_number,
        'source_file_path': source_file_path,
        'relative_path': relative_path,
    }


def parse_data(root, path):
    parts = path.relative_to(root).parts
    if parts and parts[-1] == '__init__.py':
        parts = parts[:-1]

    if parts[-1].endswith('.py'):
        parts = parts[:-1] + (parts[-1][:-3],)
    module_full_name = '.'.join(parts)
    module_display_name = parts[-1]
    module_id = get_next_id()

    MODULE_NAME_TO_ID[module_full_name] = module_id

    module_parent_id = None
    if len(parts) > 1:
        module_parent_id = MODULE_NAME_TO_ID.get('.'.join(parts[:-1]), None)
    else:
        module_parent_id = None

    rel_path = path.relative_to(root)

    common = {
        'source_file_path': str(path),
        'relative_path': str(rel_path),
    }

    with path.open('r') as f:
        module = ast.parse(f.read())
        yield get_line(
            id=module_id,
            type='module',
            name=module_display_name,
            docstring=ast.get_docstring(module),
            parent_id=module_parent_id,
            **common)
        for node in module.body:
            if isinstance(node, ast.FunctionDef):
                yield get_line(
                    id=get_next_id(),
                    type='function',
                    name=node.name,
                    docstring=ast.get_docstring(node),
                    parent_id=module_id,
                    string_inside_parens=_read_fn_args(node),
                    return_value=_read_fn_return_value(node),
                    line_number=node.lineno,
                    **common)
            elif isinstance(node, ast.ClassDef):
                class_id = get_next_id()
                yield get_line(
                    id=class_id,
                    type='class',
                    name=node.name,
                    docstring=ast.get_docstring(node),
                    parent_id=module_id,
                    string_inside_parens=_read_cls_bases(node),
                    line_number=node.lineno,
                    **common)

                last_class_node = None
                for class_node in node.body:
                    if isinstance(class_node, ast.FunctionDef):
                        yield get_line(
                            id=get_next_id(),
                            type='method',
                            name=class_node.name,
                            docstring=ast.get_docstring(class_node),
                            parent_id=class_id,
                            string_inside_parens=_read_fn_args(
                                class_node, skip_first=True),
                            return_value=_read_fn_return_value(class_node),
                            line_number=class_node.lineno,
                            **common)
                    elif isinstance(class_node, ast.Assign):
                        try:
                            name = class_node.targets[0].id
                            docstring = _read_maybe_docstring(last_class_node)
                            yield get_line(
                                id=get_next_id(),
                                type='class_var',
                                name=name,
                                docstring=docstring,
                                parent_id=class_id,
                                line_number=class_node.lineno,
                                **common)
                        except AttributeError:
                            pass
                    last_class_node = class_node


def _get_arg_string(arg, default=None, prefix=''):
    s = prefix + arg.arg
    if arg.annotation:
        s += ':' + arg.annotation
    if default is not None:
        s += '=' + _get_default_str(default)
    return s


def _get_default_str(default):
    if isinstance(default, ast.NameConstant):
        return repr(default.value)
    elif isinstance(default, ast.Num):
        return repr(default.n)
    elif isinstance(default, ast.Name):
        return default.id
    elif isinstance(default, ast.Str):
        return repr(default.s)
    else:
        # you shouldn't be using other types anyway.
        print('Could not parse arg type', default, file=sys.stderr)
        return "???"


def _read_fn_args(node, skip_first=False):
    items = []
    arguments = node.args

    num_defaults = len(arguments.defaults)
    defaults_start_i = len(arguments.args) - num_defaults
    for i, arg in enumerate(arguments.args):
        if i == 0 and skip_first:
            continue
        if i >= defaults_start_i:
            items.append(
                _get_arg_string(arg, arguments.defaults[i - defaults_start_i]))
        else:
            items.append(_get_arg_string(arg))

    if arguments.vararg:
        items.append(_get_arg_string(arguments.vararg, None, '*'))

    num_defaults = len(arguments.kw_defaults)
    defaults_start_i = len(arguments.kwonlyargs) - num_defaults
    for i, arg in enumerate(arguments.kwonlyargs):
        if i == 0 and skip_first:
            continue
        if i >= defaults_start_i:
            items.append(
                _get_arg_string(arg, arguments.kw_defaults[i - defaults_start_i]))
        else:
            items.append(_get_arg_string(arg))

    if arguments.kwarg:
        items.append(_get_arg_string(arguments.kwarg, None, '**'))
    return ', '.join(items)


def _read_fn_return_value(node):
    if node.returns is None:
        return None
    else:
        return node.returns.s


def _read_cls_bases(node):
    try:
        return ', '.join([b.id for b in node.bases])
    except AttributeError:
        log.warning(
            "Can't parse class bases for {}: {!r}".format(
                node.name, node.bases))
        return ''  # can't parse


def _read_maybe_docstring(node):
    if not node:
        return None
    if isinstance(node, ast.Expr):
        return _read_maybe_docstring(node.value)
    elif isinstance(node, ast.Str):
        return node.s


def main():
    p = argparse.ArgumentParser()
    p.add_argument('root', default=None, action='store', help=(
        'Directory in which to search for the module, or a path to a single file'))
    p.add_argument('module', nargs='?', default=None, action='store', help=(
        'Name of the module to parse (only if root is a directory)'))
    args = p.parse_args()

    root_path = pathlib.Path(args.root).resolve()

    if root_path.is_file():
        for item in list(parse_data(root_path.parent, root_path)):
            sys.stdout.write(json.dumps(item))
            sys.stdout.write('\n')
    else:
        module_root = root_path / args.module

        for py_file_path in module_root.glob('**/*.py'):
            for item in list(parse_data(root_path, py_file_path)):
                sys.stdout.write(json.dumps(item))
                sys.stdout.write('\n')


if __name__ == '__main__':
    main()

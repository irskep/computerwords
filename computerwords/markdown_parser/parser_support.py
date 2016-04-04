from .exceptions import SourceException


def log(text, *args, **kwargs):
    return
    # TODO: use logging
    print(text.format(*args, **kwargs))


class ParseError(SourceException):
    def __init__(self, token, msg=None):
        if msg is None:
            msg = "Unable to parse token {}".format(token.name)
        self.token = token
        self.msg = msg
        super().__init__(token.loc, msg)

    def __eq__(self, other):
        return (
            type(self) is type(other) and
            self.token == other.token and
            self.msg == other.msg)

    def __hash__(self):
        return hash(repr(self.token) + self.msg)


def raise_parse_error(token):
    raise ParseError("Could not parse statements at line {}, column {}".format(
        tokens[i].line, tokens[i].pos))


def none_to_duple(result, default):
    if result:
        return result
    else:
        return (None, default)


def parse_sequence(tokens, i, config, *names):
    sequence_str = ' '.join(names)
    log("Entering parse_sequence: {}", sequence_str)
    j = i
    nodes = []
    for name in names:
        result = call_parse_function(name, tokens, i, config)
        if result and result[0]:
            nodes.append(result[0])
            i = result[1]
        else:
            log("Fail {} with {}", name, tokens[i])
            return (None, j)
    log("Pass sequence {}", sequence_str)
    return nodes, i


def alternatives(*parse_fns):
    def parse_alternatives(tokens, i, config):
        log("Entering {}", parse_alternatives.__name__)
        for fn in parse_fns:
            result = fn(tokens, i, config)
            if result: return result
        return (None, i)
    return parse_alternatives


def sequence_rule(Cls, form, *sequence):
    def sequence_parser(tokens, i, config):
        (nodes, i) = parse_sequence(tokens, i, config, *sequence)
        if nodes:
            return (Cls(form, *nodes), i)
        else:
            return None
    return sequence_parser


def validate(validator, parse_fn):
    """validator may simply return False, or raise a ParseError"""
    def wrapper_fn(tokens, i, config):
        (node, i) = none_to_duple(parse_fn(tokens, i, config), i)
        if node and validator(node, config):
            return (node, i)
        else:
            return None
    return wrapper_fn


PARSE_FUNC_REGISTRY = {}
def rule(name, *fns, error_if_not_success=False):
    if len(fns) > 1:
        fn = alternatives(*fns)
    else:
        fn = fns[0]
    if error_if_not_success:
        inner_fn = fn
        def wrapper_fn(tokens, i, config):
            result = inner_fn(tokens, i, config)
            if result and result[0]:
                return result
            else:
                raise ParseError(tokens[i])
        fn = wrapper_fn
    PARSE_FUNC_REGISTRY[name] = fn
    fn.__name__ = 'parse_' + name
    return fn


def call_parse_function(name, tokens, i, config): 
    return PARSE_FUNC_REGISTRY[name](tokens, i, config)

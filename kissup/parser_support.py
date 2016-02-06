def log(text):
    # TODO: use logging
    print(text)


class ParseError(Exception):
    def __init__(self, token, msg):
        super().__init__("Line {} col {}: {}".format(token.line, token.pos, msg))


def multi_rule(*parse_fns):
    def parse(tokens, i):
        log("Entering {}".format(parse.__name__))
        for fn in parse_fns:
            result = fn(tokens, i)
            if result: return result
        return (None, i)
    return parse

def parse_sequence(tokens, i, *names):
    log("Entering parse_sequence: {}".format(' '.join(names)))
    j = i
    nodes = []
    for name in names:
        result = call_parse_function(name, tokens, i)
        if result:
            nodes.append(result[0])
            i = result[1]
        else:
            return (None, j)
    return nodes, i

def none_to_duple(result, default):
    if result:
        return result
    else:
        return (None, default)

def sequence_rule(Cls, form, *sequence):
    def sequence_parser(tokens, i):
        (nodes, i) = parse_sequence(tokens, i, *sequence)
        if nodes:
            return (Cls(form, *nodes), i)
        else:
            return None
    return sequence_parser


PARSE_FUNC_REGISTRY = {}
def rule(name, fn):
    PARSE_FUNC_REGISTRY[name] = fn
    fn.__name__ = 'parse_' + name
    return fn


def call_parse_function(name, token, i):
    return PARSE_FUNC_REGISTRY[name](token, i)
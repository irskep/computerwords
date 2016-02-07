def log(text, *args, **kwargs):
    return
    # TODO: use logging
    print(text.format(*args, **kwargs))


class ParseError(Exception):
    def __init__(self, token, msg):
        super().__init__("Line {} col {}: {}".format(token.line, token.pos, msg))


def raise_parse_error(token):
    raise ParseError("Could not parse statements at line {}, column {}".format(
        tokens[i].line, tokens[i].pos))


def none_to_duple(result, default):
    if result:
        return result
    else:
        return (None, default)


def parse_sequence(tokens, i, *names):
    sequence_str = ' '.join(names)
    log("Entering parse_sequence: {}", sequence_str)
    j = i
    nodes = []
    for name in names:
        result = call_parse_function(name, tokens, i)
        if result and result[0]:
            nodes.append(result[0])
            i = result[1]
        else:
            log("Fail {} with {}", name, tokens[i])
            return (None, j)
    log("Pass sequence {}", sequence_str)
    return nodes, i


def alternatives(*parse_fns):
    def parse_alternatives(tokens, i):
        log("Entering {}", parse_alternatives.__name__)
        for fn in parse_fns:
            result = fn(tokens, i)
            if result: return result
        return (None, i)
    return parse_alternatives


def sequence_rule(Cls, form, *sequence):
    def sequence_parser(tokens, i):
        (nodes, i) = parse_sequence(tokens, i, *sequence)
        if nodes:
            return (Cls(form, *nodes), i)
        else:
            return None
    return sequence_parser


PARSE_FUNC_REGISTRY = {}
def rule(name, *fns):
    if len(fns) > 1:
        fn = alternatives(*fns)
    else:
        fn = fns[0]
    PARSE_FUNC_REGISTRY[name] = fn
    fn.__name__ = 'parse_' + name
    return fn


def call_parse_function(name, token, i): 
    return PARSE_FUNC_REGISTRY[name](token, i)
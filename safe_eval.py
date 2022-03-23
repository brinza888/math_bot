import ast
import operator as op
from functools import wraps


def args_limit(*limits):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            check = True
            for arg, limit in zip(args, limits):
                check = check and (arg != -1 and arg > limit)
            if check:
                raise ValueError("Argument limit reached!")
            return func(*args, **kwargs)
        return wrapper
    return decorator


# supported operators
LINE_LIMIT = 1000
LIMIT = 50 ** 50
POW_LIMIT = 30

operators = {
    ast.Add: args_limit(LIMIT, LIMIT)(op.add),
    ast.Sub: args_limit(LIMIT, LIMIT)(op.sub),
    ast.Mult: args_limit(LIMIT, LIMIT)(op.mul),
    ast.Div: args_limit(LIMIT, LIMIT)(op.truediv),
    ast.FloorDiv: args_limit(LIMIT, LIMIT)(op.floordiv),
    ast.Pow: args_limit(POW_LIMIT, POW_LIMIT)(op.pow),
    ast.BitXor: args_limit(LIMIT, LIMIT)(op.xor),
    ast.BitAnd: args_limit(LIMIT, LIMIT)(op.and_),
    ast.BitOr: args_limit(LIMIT, LIMIT)(op.or_),
    ast.USub: args_limit(LIMIT, LIMIT)(op.neg),
}


def safe_eval(expr):
    if len(expr) >= LINE_LIMIT:
        raise ValueError(f"Eval string length limit reached!")
    return _eval(ast.parse(expr, mode='eval').body)


def _eval(node):
    if isinstance(node, ast.Num):  # <number>
        return node.n
    elif isinstance(node, ast.BinOp):  # <left> <operator> <right>
        return operators[type(node.op)](_eval(node.left), _eval(node.right))
    elif isinstance(node, ast.UnaryOp):  # <operator> <operand> e.g., -1
        return operators[type(node.op)](_eval(node.operand))
    else:
        raise TypeError(node)


if __name__ == '__main__':
    while True:
        try:
            print(safe_eval(input("> ")))
        except ValueError as ex:
            print(ex)
        except KeyboardInterrupt:
            print("Bye!")
            break

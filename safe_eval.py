# -*- coding: utf-8 -*-

# Copyright (C) 2021-2022 Ilya Bezrukov, Stepan Chizhov, Artem Grishin
#
# This file is part of math_bot.
#
# math_bot is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 2 of the License, or
# any later version.
#
# math_bot is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

import ast
import operator as op
from functools import wraps


class LimitError (ValueError):
    """ Base class for limit exceptions """
    pass


class ExpressionLimitError (LimitError):
    """ Raises if length of expression more than length limit """
    pass


class ArgumentLimitError (LimitError):
    """ Raises if numeric argument more than argument limit for this operation """
    pass


def args_limit(*limits):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            check = True
            for arg, limit in zip(args, limits):
                check = check and (arg != -1 and arg > limit)
            if check:
                raise ArgumentLimitError("Argument size limit exceeded")
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
        raise ExpressionLimitError("Expression size limit exceeded")
    return _eval(ast.parse(expr, mode="eval").body)


def _eval(node):
    if isinstance(node, ast.Num):  # <number>
        return node.n
    elif isinstance(node, ast.BinOp):  # <left> <operator> <right>
        return operators[type(node.op)](_eval(node.left), _eval(node.right))
    elif isinstance(node, ast.UnaryOp):  # <operator> <operand> e.g., -1
        return operators[type(node.op)](_eval(node.operand))
    else:
        raise TypeError(node)


if __name__ == "__main__":
    print("Copyright (C) 2021-2022 Ilya Bezrukov, Stepan Chizhov, Artem Grishin")
    print("Licensed under GNU GPL-2.0-or-later")
    while True:
        try:
            print(safe_eval(input("> ")))
        except (ValueError, SyntaxError, TypeError) as ex:
            print(ex.__class__.__name__, ex)
        except KeyboardInterrupt:
            print("Bye!")
            break
